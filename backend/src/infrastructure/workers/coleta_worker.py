import logging
import asyncio
from celery import shared_task
from sqlmodel import Session
from infrastructure.database import engine
from application.services.coletar_em_lote_service import ColetarEmLoteService

logger = logging.getLogger(__name__)


@shared_task(name="coletar_proposicoes_diario")
def task_coletar_proposicoes_diario():
    """
    Task diária do Celery para buscar proposições em lote (Câmara e Senado).
    Delega a orquestração para o Application Service.
    """
    logger.info("Iniciando worker: task_coletar_proposicoes_diario")

    async def _run():
        with Session(engine) as session:
            service = ColetarEmLoteService(session)
            return await service.executar_coleta_diaria()

    resumo = asyncio.run(_run())

    logger.info(f"Worker finalizado. Resumo: {resumo}")
    return resumo
