import asyncio
import logging

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError, Retry
from sqlmodel import Session

from application.services.coletar_em_lote_service import ColetarEmLoteService
from application.services.reconstruir_periodos_service import ReconstruirPeriodosService
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.database import engine
from infrastructure.repositories.sql_apensamento_repository import (
    SQLApensamentoRepository,
)
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_log_coleta_repository import (
    SQLLogColetaRepository,
)
from infrastructure.repositories.sql_orgao_legislativo_repository import (
    SQLOrgaoLegislativoRepository,
)
from infrastructure.repositories.sql_periodo_fase_repository import (
    SQLPeriodoFaseRepository,
)
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="coletar_proposicoes_diario", max_retries=3)
def task_coletar_proposicoes_diario(self):
    """
    Task diária do Celery para buscar proposições em lote (Câmara e Senado).
    Delega a orquestração para o Application Service.
    """
    job_id = self.request.id or "coleta-manual"
    nome_job = "coleta_diaria"
    logger.info(f"Iniciando worker: task_coletar_proposicoes_diario (job_id: {job_id})")

    from infrastructure.repositories.sql_auditoria_coleta_repository import (
        SQLAuditoriaColetaRepository,
    )

    async def _run():
        with Session(engine) as session:
            auditoria_repo = SQLAuditoriaColetaRepository(session)
            auditoria_repo.registrar_inicio(job_id, nome_job)

            repository = SQLProposicaoRepository(session)
            evento_repo = SQLEventoTramitacaoRepository(session)
            fase_repo = SQLFaseAnaliticaRepository(session)
            orgao_repo = SQLOrgaoLegislativoRepository(session)
            apensamento_repo = SQLApensamentoRepository(session)
            log_repo = SQLLogColetaRepository(session)
            periodo_repo = SQLPeriodoFaseRepository(session)
            camara_adapter = CamaraAdapter()
            senado_adapter = SenadoAdapter()

            reconstruir_service = ReconstruirPeriodosService(
                periodo_repo=periodo_repo,
                evento_repo=evento_repo,
                fase_repo=fase_repo,
                proposicao_repo=repository,
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
            )

            try:
                resumo = await service.executar_coleta_diaria()

                itens_processados = resumo.get("camara", {}).get(
                    "itens_coletados", 0
                ) + resumo.get("senado", {}).get("itens_coletados", 0)

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

                auditoria_repo.registrar_fim(
                    job_id, status_geral, itens_processados, erro_msg
                )
                return resumo
            except Exception as e:
                auditoria_repo.registrar_fim(job_id, "falha", 0, str(e))
                raise

    try:
        resumo = asyncio.run(_run())

        camara_status = resumo.get("camara", {}).get("status")
        senado_status = resumo.get("senado", {}).get("status")
        if camara_status == "falha" and senado_status == "falha":
            delay = 60 * (2**self.request.retries)
            logger.warning(
                f"Coleta falhou totalmente nas duas fontes. Agendando retry em {delay}s..."
            )
            raise self.retry(exc=Exception("Coleta falhou totalmente"), countdown=delay)

        logger.info(f"Worker finalizado. Resumo: {resumo}")
        return resumo
    except Exception as exc:
        if isinstance(exc, (Retry, MaxRetriesExceededError)):
            raise exc

        delay = 60 * (2**self.request.retries)
        try:
            raise self.retry(exc=exc, countdown=delay)
        except MaxRetriesExceededError:
            logger.exception("Limite máximo de retries excedido para a coleta diária.")
            raise exc from None


@shared_task(name="backfill_emendas_issue_253")
def task_backfill_emendas():
    """
    Task do Celery para rodar o backfill de emendas em background.
    Disparada após migrations ou via dashboard.
    """
    logger.info("Iniciando worker: task_backfill_emendas")
    from application.services.backfill_emendas_service import BackfillEmendasService

    async def _run():
        with Session(engine) as session:
            camara = CamaraAdapter()
            senado = SenadoAdapter()
            service = BackfillEmendasService(session, camara, senado)
            return await service.executar()

    resumo = asyncio.run(_run())
    logger.info(f"Worker finalizado. Resumo: {resumo}")
    return resumo
