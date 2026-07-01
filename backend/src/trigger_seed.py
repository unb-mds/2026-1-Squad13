import logging
import sys

from infrastructure.workers.celery_app import celery_app  # noqa: F401
from infrastructure.workers.coleta_worker import task_preencher_lacunas

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("trigger_seed")


def trigger():
    try:
        logger.info(
            "📡 Enviando sinal para iniciar preenchimento de lacunas via Celery..."
        )
        result = task_preencher_lacunas.delay()
        logger.info(f"✅ Task enfileirada com sucesso! ID: {result.id}")
        logger.info(
            "🚀 O processamento continuará em background nos workers do Celery."
        )
    except Exception as e:
        logger.error(f"❌ Falha ao enfileirar task no Celery: {e}")
        sys.exit(1)


if __name__ == "__main__":
    trigger()
