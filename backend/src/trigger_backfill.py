import logging
import sys

from infrastructure.workers.celery_app import celery_app  # noqa: F401
from infrastructure.workers.coleta_worker import task_backfill_emendas

# Configuração mínima de logging para saída limpa no terminal
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("trigger_backfill")


def trigger():
    """
    Dispara a task de backfill no Celery de forma assíncrona.
    """
    try:
        logger.info("📡 Enviando sinal para iniciar backfill de emendas (Celery)...")
        # .delay() enfileira a task e retorna imediatamente
        result = task_backfill_emendas.delay()
        logger.info(f"✅ Task enfileirada com ID: {result.id}")
        logger.info(
            "🚀 O processamento continuará em background nos workers do Celery."
        )
    except Exception as e:
        logger.error(f"❌ Falha ao enfileirar task: {e}")
        sys.exit(1)


if __name__ == "__main__":
    trigger()
