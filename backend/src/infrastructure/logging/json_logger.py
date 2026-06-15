import json
import logging
from datetime import UTC, datetime
from typing import Any

from celery import current_task


class JSONFormatter(logging.Formatter):
    """
    Formatador de logs customizado para exportação estruturada em formato JSON.
    Inclui correlação por job_id quando disponível no contexto.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Injeta job_id se houver no record (via LoggerAdapter ou Filter)
        if hasattr(record, "job_id"):
            log_data["job_id"] = record.job_id

        # Captura stack trace se houver erro/exceção
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class CeleryTaskFilter(logging.Filter):
    """
    Filtro que injeta o job_id (ID da Task do Celery) em todos os registros de log.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        task = current_task
        if task and task.request:
            record.job_id = task.request.id
        else:
            record.job_id = "no-job"
        return True


def setup_celery_logger(logger: logging.Logger, **kwargs: Any) -> None:
    """
    Configura o formatador JSON e o filtro de tarefa nos handlers de logs do Celery.
    """
    for handler in logger.handlers:
        handler.setFormatter(JSONFormatter())
        handler.addFilter(CeleryTaskFilter())
