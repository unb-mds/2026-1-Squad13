import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from infrastructure.workers.coleta_worker import task_coletar_proposicoes_diario

@patch("infrastructure.workers.coleta_worker.ColetarEmLoteService")
@patch("infrastructure.workers.coleta_worker.Session")
def test_task_coletar_proposicoes_diario(mock_session_cls, mock_service_cls):
    """Verifica se a task do Celery instancia o serviço e executa a coleta."""
    mock_service_instance = mock_service_cls.return_value
    # IMPORTANTE: Como o método é async, precisamos que o mock retorne uma corrotina
    mock_service_instance.executar_coleta_diaria = AsyncMock(return_value={"status": "ok"})
    
    # Mock do context manager da Session
    mock_session_instance = mock_session_cls.return_value.__enter__.return_value

    resumo = task_coletar_proposicoes_diario()

    assert resumo == {"status": "ok"}
    mock_service_cls.assert_called_once_with(mock_session_instance)
    mock_service_instance.executar_coleta_diaria.assert_called_once()
