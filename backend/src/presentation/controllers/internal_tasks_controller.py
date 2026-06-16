import logging
import uuid

from fastapi import APIRouter, Depends
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


@router.post("/tarefas/coleta")
async def executar_coleta(session: Session = Depends(get_session)):
    """
    Dispara a coleta diária de proposições (Câmara + Senado).
    Autenticado via X-Internal-Token. Chamado pelo GitHub Actions cron.
    """
    job_id = str(uuid.uuid4())
    nome_job = "coleta_diaria"
    logger.info(f"Iniciando coleta via endpoint interno (job_id: {job_id})")

    auditoria_repo = SQLAuditoriaColetaRepository(session)
    auditoria_repo.registrar_inicio(job_id, nome_job)

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

    redis_raw = get_redis_client()
    cache_provider = RedisClient(redis_raw)

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

    try:
        resumo = await service.executar_coleta_diaria()

        itens_processados = resumo.get("camara", {}).get("itens_coletados", 0) + resumo.get(
            "senado", {}
        ).get("itens_coletados", 0)

        camara_status = resumo.get("camara", {}).get("status")
        senado_status = resumo.get("senado", {}).get("status")

        if camara_status == "sucesso" and senado_status == "sucesso":
            status_geral = "sucesso"
            erro_msg = None
        elif camara_status == "falha" and senado_status == "falha":
            status_geral = "falha"
            erro_msg = f"Falha na Camara ({resumo['camara']['erro']}) e Senado ({resumo['senado']['erro']})"
        else:
            status_geral = "parcial"
            erro_msg = f"Camara: {camara_status}. Senado: {senado_status}."

        auditoria_repo.registrar_fim(job_id, status_geral, itens_processados, erro_msg)

        try:
            cache_provider.invalidate("dashboard:")
        except Exception as cache_err:
            logger.error(f"Falha ao invalidar cache do dashboard após coleta: {cache_err}")

        logger.info(f"Coleta via endpoint interno finalizada. Resumo: {resumo}")
        return {"job_id": job_id, "status": status_geral, "resumo": resumo}

    except Exception as e:
        auditoria_repo.registrar_fim(job_id, "falha", 0, str(e))
        logger.exception(f"Erro na coleta via endpoint interno (job_id: {job_id})")
        raise


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
