import json
import logging
from unittest.mock import MagicMock, patch

from infrastructure.logging.json_logger import CeleryTaskFilter, JSONFormatter


def test_json_formatter_format():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Mensagem de teste",
        args=(),
        exc_info=None,
    )

    # Injeta manualmente o job_id para simular o LoggerAdapter
    record.job_id = "test-job-id"

    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["level"] == "INFO"
    assert data["logger"] == "test_logger"
    assert data["message"] == "Mensagem de teste"
    assert data["job_id"] == "test-job-id"
    assert "timestamp" in data


def test_celery_task_filter():
    task_filter = CeleryTaskFilter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Mensagem de teste",
        args=(),
        exc_info=None,
    )

    # 1. Sem task ativa, deve injetar "no-job"
    with patch("infrastructure.logging.json_logger.current_task", None):
        assert task_filter.filter(record) is True
        assert record.job_id == "no-job"

    # 2. Com task ativa contendo request.id, deve injetar o id correto
    mock_task = MagicMock()
    mock_task.request.id = "celery-uuid-123"
    with patch("infrastructure.logging.json_logger.current_task", mock_task):
        assert task_filter.filter(record) is True
        assert record.job_id == "celery-uuid-123"
