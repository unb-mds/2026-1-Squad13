from unittest.mock import AsyncMock, patch

from infrastructure.workers.coleta_worker import task_coletar_proposicoes_diario


@patch("infrastructure.workers.coleta_worker.ColetarEmLoteService")
@patch("infrastructure.workers.coleta_worker.Session")
def test_task_coletar_proposicoes_diario(mock_session_cls, mock_service_cls):
    """Verifica se a task do Celery instancia o serviço e executa a coleta."""
    mock_service_instance = mock_service_cls.return_value
    # IMPORTANTE: Como o método é async, precisamos que o mock retorne uma corrotina
    mock_service_instance.executar_coleta_diaria = AsyncMock(
        return_value={"status": "ok"}
    )

    # Mock do context manager da Session
    _ = mock_session_cls.return_value.__enter__.return_value

    resumo = task_coletar_proposicoes_diario()

    assert resumo == {"status": "ok"}
    mock_service_cls.assert_called_once()
    kwargs = mock_service_cls.call_args.kwargs
    assert "repository" in kwargs
    assert "evento_repo" in kwargs
    assert "fase_repo" in kwargs
    assert "orgao_repo" in kwargs
    assert "apensamento_repo" in kwargs
    assert "log_repo" in kwargs
    assert "camara_adapter" in kwargs
    assert "senado_adapter" in kwargs
    mock_service_instance.executar_coleta_diaria.assert_called_once()
