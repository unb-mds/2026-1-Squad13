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
    logger.info("📅 INICIANDO WORKER: Coleta Diária em Lote (Câmara e Senado)")

    async def _run():
        with Session(engine) as session:
            service = ColetarEmLoteService(session)
            return await service.executar_coleta_diaria()

    try:
        resumo = asyncio.run(_run())
        logger.info(f"✅ Worker finalizado com sucesso. Resumo: {resumo}")
        return resumo
    except Exception as e:
        logger.exception(f"❌ Erro crítico no worker de coleta: {e}")
        raise


@shared_task(name="worker_heartbeat")
def task_worker_heartbeat():
    """
    Tarefa simples para confirmar que o worker e o beat estão operacionais.
    """
    logger.info("💓 HEARTBEAT: Worker operacional e processando tarefas.")
    return "OK"
