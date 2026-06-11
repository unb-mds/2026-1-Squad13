from celery import Celery
from celery.schedules import crontab
from celery.signals import after_setup_logger, after_setup_task_logger

from infrastructure.config import settings
from infrastructure.logging.json_logger import setup_celery_logger

celery_app = Celery(
    "monitor_legislativo",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "infrastructure.workers.coleta_worker",
        "infrastructure.workers.metricas_worker",
    ],
)

celery_app.conf.timezone = "America/Sao_Paulo"
celery_app.conf.beat_schedule = {
    "coleta-diaria-camara-senado": {
        "task": "coletar_proposicoes_diario",
        "schedule": crontab(minute=37, hour=2),
    },
    "recalcular-baselines-diario": {
        "task": "recalcular_baselines_diario",
        "schedule": crontab(minute=0, hour=3),
    },
    "processar-metricas-diario": {
        "task": "processar_metricas_todas_ativas",
        "schedule": crontab(minute=0, hour=4),
    },
}

# --- Setup de Logging Estruturado para Produção ---


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    setup_celery_logger(logger, **kwargs)


@after_setup_task_logger.connect
def setup_task_loggers(logger, *args, **kwargs):
    setup_celery_logger(logger, **kwargs)
