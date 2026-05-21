from celery import Celery
from celery.schedules import crontab
from infrastructure.config import settings

app = Celery(
    "monitor_legislativo",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Configurações otimizadas do Celery
app.conf.update(
    timezone="America/Sao_Paulo",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    # Garante que o worker carregue as tasks do módulo de coleta
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)

# Agendamento de tarefas (Beat)
app.conf.beat_schedule = {
    "coleta-diaria-camara-senado": {
        "task": "coletar_proposicoes_diario",
        "schedule": crontab(minute=37, hour=2),  # Executa diariamente às 02:37 AM
    },
    "worker-heartbeat": {
        "task": "worker_heartbeat",
        "schedule": crontab(minute="*/30"),  # Ping a cada 30 minutos para log
    },
}

# Auto-descoberta de tarefas em módulos que tenham o decorator @shared_task
app.autodiscover_tasks(["infrastructure.workers"])
