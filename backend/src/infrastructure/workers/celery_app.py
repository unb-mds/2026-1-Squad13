from celery import Celery
from celery.schedules import crontab

from infrastructure.config import settings

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
