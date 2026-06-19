import asyncio
import logging
import uuid

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from application.services.atualizar_cobertura_service import AtualizarCoberturaService
from application.services.coletar_em_lote_service import ColetarEmLoteService
from application.services.processar_metricas_service import ProcessarMetricasService
from application.services.recalcular_baselines_service import RecalcularBaselinesService
from application.services.reconstruir_periodos_service import ReconstruirPeriodosService
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.cache.redis_client import RedisClient
from infrastructure.database import get_redis_client, get_session
from infrastructure.repositories.sql_apensamento_repository import (
    SQLApensamentoRepository,
)
from infrastructure.repositories.sql_auditoria_coleta_repository import (
    SQLAuditoriaColetaRepository,
)
from infrastructure.repositories.sql_baseline_tramitacao_repository import (
    SQLBaselineTramitacaoRepository,
)
from infrastructure.repositories.sql_cobertura_snapshot_repository import (
    SQLCoberturaSnapshotRepository,
)
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_log_coleta_repository import SQLLogColetaRepository
from infrastructure.repositories.sql_orgao_legislativo_repository import (
    SQLOrgaoLegislativoRepository,
)
from infrastructure.repositories.sql_periodo_fase_repository import (
    SQLPeriodoFaseRepository,
)
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)
from presentation.internal_auth import verify_internal_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/internal",
    tags=["Internal Tasks"],
    dependencies=[Depends(verify_internal_token)],
)


_LUA_RELEASE_LOCK = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
"""


@router.post("/tarefas/coleta")
async def executar_coleta(session: Session = Depends(get_session)):
    """
    Dispara a coleta diária de proposições (Câmara + Senado).
    Autenticado via X-Internal-Token. Chamado pelo GitHub Actions cron.
    """
    job_id = str(uuid.uuid4())
    nome_job = "coleta_diaria"

    auditoria_repo = SQLAuditoriaColetaRepository(session)
    redis_raw = get_redis_client()
    cache_provider = RedisClient(redis_raw)

    # Fix 3 — lock anti-sobreposição (TTL 1200s = 20 min)
    token = str(uuid.uuid4())
    chave_lock = "coleta:lock:coleta_diaria"
    if not cache_provider.set_nx(chave_lock, token, ttl_seconds=1200):
        logger.warning("Coleta diária já em execução. Bloqueando sobreposição.")
        return {"status": "overlap_bloqueado"}

    # Fix 4 — recuperar execuções travadas da rodada anterior
    travadas = auditoria_repo.marcar_travadas_como_timeout(nome_job, minutos=30)
    if travadas:
        logger.warning(f"{travadas} execução(ões) travada(s) marcada(s) como timeout.")

    auditoria_repo.registrar_inicio(job_id, nome_job)
    logger.info(f"Iniciando coleta via endpoint interno (job_id: {job_id})")

    repository = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    fase_repo = SQLFaseAnaliticaRepository(session)
    orgao_repo = SQLOrgaoLegislativoRepository(session)
    apensamento_repo = SQLApensamentoRepository(session)
    log_repo = SQLLogColetaRepository(session)
    periodo_repo = SQLPeriodoFaseRepository(session)
    cobertura_repo = SQLCoberturaSnapshotRepository(session)

    camara_adapter = CamaraAdapter()
    senado_adapter = SenadoAdapter()

    reconstruir_service = ReconstruirPeriodosService(
        periodo_repo=periodo_repo,
        evento_repo=evento_repo,
        fase_repo=fase_repo,
        proposicao_repo=repository,
    )
    cobertura_service = AtualizarCoberturaService(
        cobertura_repo=cobertura_repo,
        proposicao_repo=repository,
        camara_adapter=camara_adapter,
        senado_adapter=senado_adapter,
    )
    service = ColetarEmLoteService(
        repository=repository,
        evento_repo=evento_repo,
        fase_repo=fase_repo,
        orgao_repo=orgao_repo,
        apensamento_repo=apensamento_repo,
        log_repo=log_repo,
        camara_adapter=camara_adapter,
        senado_adapter=senado_adapter,
        reconstruir_service=reconstruir_service,
        cobertura_service=cobertura_service,
        cache_provider=cache_provider,
    )

    # Fix 1 — variáveis de estado para o finally (garante registrar_fim sempre executado)
    status_para_registrar = "falha"
    itens_para_registrar = 0
    erro_para_registrar: str | None = None
    resumo_para_retorno: dict = {}

    try:
        # Fix 2 — timeout global de 240s (margem de 60s antes do cron do GA matar)
        resumo = await asyncio.wait_for(service.executar_coleta_diaria(), timeout=240)
        resumo_para_retorno = resumo

        itens_para_registrar = resumo.get("camara", {}).get(
            "itens_coletados", 0
        ) + resumo.get("senado", {}).get("itens_coletados", 0)

        camara_status = resumo.get("camara", {}).get("status")
        senado_status = resumo.get("senado", {}).get("status")

        if camara_status == "sucesso" and senado_status == "sucesso":
            status_para_registrar = "sucesso"
        elif camara_status == "falha" and senado_status == "falha":
            status_para_registrar = "falha"
            erro_para_registrar = (
                f"Falha na Camara ({resumo['camara']['erro']}) "
                f"e Senado ({resumo['senado']['erro']})"
            )
        else:
            status_para_registrar = "parcial"
            erro_para_registrar = f"Camara: {camara_status}. Senado: {senado_status}."

        try:
            cache_provider.invalidate("dashboard:")
        except Exception as cache_err:
            logger.error(
                f"Falha ao invalidar cache do dashboard após coleta: {cache_err}"
            )

        logger.info(f"Coleta via endpoint interno finalizada. Resumo: {resumo}")
        return {
            "job_id": job_id,
            "status": status_para_registrar,
            "resumo": resumo_para_retorno,
        }

    except TimeoutError:
        erro_para_registrar = "timeout interno de 240s excedido"
        logger.error(f"Timeout na coleta via endpoint interno (job_id: {job_id})")
        raise

    except asyncio.CancelledError:
        erro_para_registrar = "request cancelado externamente (CancelledError)"
        logger.error(
            f"CancelledError na coleta via endpoint interno (job_id: {job_id})"
        )
        raise

    except Exception as e:
        erro_para_registrar = str(e)
        logger.exception(f"Erro na coleta via endpoint interno (job_id: {job_id})")
        raise

    finally:
        try:
            auditoria_repo.registrar_fim(
                job_id, status_para_registrar, itens_para_registrar, erro_para_registrar
            )
        except Exception as fim_err:
            logger.error(
                f"Falha ao registrar_fim, tentando após rollback (job_id: {job_id}): {fim_err}"
            )
            try:
                session.rollback()
                auditoria_repo.registrar_fim(
                    job_id,
                    status_para_registrar,
                    itens_para_registrar,
                    erro_para_registrar,
                )
            except Exception as fim_err2:
                logger.critical(
                    f"Falha crítica ao registrar_fim mesmo após rollback (job_id: {job_id}): {fim_err2}"
                )
        try:
            cache_provider.eval_lua(_LUA_RELEASE_LOCK, [chave_lock], [token])
        except Exception as lock_err:
            logger.error(f"Erro ao liberar o lock da coleta diária: {lock_err}")


@router.post("/tarefas/baselines")
def executar_baselines(session: Session = Depends(get_session)):
    """
    Dispara o recálculo de baselines de tramitação.
    Autenticado via X-Internal-Token. Chamado pelo GitHub Actions cron.
    """
    logger.info("Iniciando recálculo de baselines via endpoint interno")

    prop_repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    fase_repo = SQLFaseAnaliticaRepository(session)
    baseline_repo = SQLBaselineTramitacaoRepository(session)

    service = RecalcularBaselinesService(
        proposicao_repo=prop_repo,
        evento_repo=evento_repo,
        fase_repo=fase_repo,
        baseline_repo=baseline_repo,
    )
    resumo = service.executar()

    try:
        redis_raw = get_redis_client()
        cache_provider = RedisClient(redis_raw)
        cache_provider.invalidate("dashboard:")
    except Exception as cache_err:
        logger.error(f"Falha ao invalidar cache após baselines: {cache_err}")

    logger.info(f"Baselines via endpoint interno finalizados. Resumo: {resumo}")
    return {"status": "sucesso", "resumo": resumo}


@router.post("/tarefas/metricas")
def executar_metricas(session: Session = Depends(get_session)):
    """
    Dispara o processamento de métricas de todas as proposições ativas.
    Autenticado via X-Internal-Token. Chamado pelo GitHub Actions cron.
    """
    logger.info("Iniciando processamento de métricas via endpoint interno")

    prop_repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    fase_repo = SQLFaseAnaliticaRepository(session)
    baseline_repo = SQLBaselineTramitacaoRepository(session)

    service = ProcessarMetricasService(
        proposicao_repo=prop_repo,
        evento_repo=evento_repo,
        fase_repo=fase_repo,
        baseline_repo=baseline_repo,
    )
    resumo = service.executar()

    try:
        redis_raw = get_redis_client()
        cache_provider = RedisClient(redis_raw)
        cache_provider.invalidate("dashboard:")
    except Exception as cache_err:
        logger.error(f"Falha ao invalidar cache após métricas: {cache_err}")

    logger.info(f"Métricas via endpoint interno finalizadas. Resumo: {resumo}")
    return {"status": "sucesso", "resumo": resumo}


@router.post("/tarefas/reconstruir-periodos")
def executar_reconstruir_periodos(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """
    Reconstrói períodos analíticos para proposições que não os possuem.
    Autenticado via X-Internal-Token. Deve ser chamado em lotes via
    ?offset=&limit= (máx 100) até que "restantes" retorne 0.
    O filtro WHERE (sem período) é aplicado antes do offset/limit, garantindo
    que proposições já reconstruídas saiam naturalmente do conjunto.
    """
    from sqlmodel import func, select

    from infrastructure.database.models.periodo_fase_model import PeriodoFaseModel
    from infrastructure.database.models.proposicao_model import ProposicaoModel

    logger.info(
        f"Iniciando reconstrução de períodos analíticos (offset={offset}, limit={limit})"
    )

    periodo_repo = SQLPeriodoFaseRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    fase_repo = SQLFaseAnaliticaRepository(session)
    prop_repo = SQLProposicaoRepository(session)

    reconstruir_service = ReconstruirPeriodosService(
        periodo_repo=periodo_repo,
        evento_repo=evento_repo,
        fase_repo=fase_repo,
        proposicao_repo=prop_repo,
    )

    ids_com_periodo = select(PeriodoFaseModel.proposicao_id)
    filtro_sem_periodo = ProposicaoModel.id.not_in(ids_com_periodo)

    total_restantes = session.exec(
        select(func.count(ProposicaoModel.id)).where(filtro_sem_periodo)
    ).one()

    props_lote = session.exec(
        select(ProposicaoModel).where(filtro_sem_periodo).offset(offset).limit(limit)
    ).all()

    sucesso = 0
    falhas = []

    for prop in props_lote:
        prop_id = prop.id
        try:
            reconstruir_service.reconstruir_para_proposicao(prop_id)
            sucesso += 1
        except Exception as e:
            session.rollback()
            logger.error(f"Falha ao reconstruir proposição {prop_id}: {e}")
            falhas.append({"id": prop_id, "erro": str(e)})

    restantes_apos_lote = max(0, total_restantes - sucesso)

    logger.info(
        f"Lote finalizado. Sucesso: {sucesso}/{len(props_lote)}. "
        f"Falhas: {len(falhas)}. Restantes estimados: {restantes_apos_lote}."
    )
    return {
        "status": "sucesso" if not falhas else "parcial",
        "processadas": sucesso,
        "falhas": len(falhas),
        "detalhes_falhas": falhas,
        "restantes": restantes_apos_lote,
    }
