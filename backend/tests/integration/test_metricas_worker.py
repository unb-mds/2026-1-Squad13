from unittest.mock import patch

from infrastructure.workers.metricas_worker import (
    task_processar_metricas_todas_ativas,
    task_recalcular_baselines_diario,
)


@patch("infrastructure.workers.metricas_worker.RecalcularBaselinesService")
@patch("infrastructure.workers.metricas_worker.Session")
def test_task_recalcular_baselines_diario(mock_session_cls, mock_service_cls):
    """Verifica se a task do Celery instancia o serviço e executa o recálculo de baselines."""
    mock_service_instance = mock_service_cls.return_value
    mock_service_instance.executar.return_value = {"total_iar_criados": 5}

    resumo = task_recalcular_baselines_diario()

    assert resumo == {"total_iar_criados": 5}
    mock_service_cls.assert_called_once()
    mock_service_instance.executar.assert_called_once()


@patch("infrastructure.workers.metricas_worker.ProcessarMetricasService")
@patch("infrastructure.workers.metricas_worker.Session")
def test_task_processar_metricas_todas_ativas(mock_session_cls, mock_service_cls):
    """Verifica se a task do Celery instancia o serviço e executa o processamento de métricas."""
    mock_service_instance = mock_service_cls.return_value
    mock_service_instance.executar.return_value = {"processados": 10}

    resumo = task_processar_metricas_todas_ativas()

    assert resumo == {"processados": 10}
    mock_service_cls.assert_called_once()
    mock_service_instance.executar.assert_called_once()


@patch("infrastructure.workers.metricas_worker.RecalcularBaselinesService")
@patch("infrastructure.workers.metricas_worker.Session")
def test_task_recalcular_baselines_diario_error(mock_session_cls, mock_service_cls):
    """Verifica se a task do Celery trata erros corretamente."""
    mock_service_instance = mock_service_cls.return_value
    mock_service_instance.executar.side_effect = Exception("Erro genérico")

    try:
        task_recalcular_baselines_diario()
    except Exception as e:
        assert str(e) == "Erro genérico"


@patch("infrastructure.workers.metricas_worker.ProcessarMetricasService")
@patch("infrastructure.workers.metricas_worker.Session")
def test_task_processar_metricas_todas_ativas_error(mock_session_cls, mock_service_cls):
    """Verifica se a task do Celery trata erros corretamente."""
    mock_service_instance = mock_service_cls.return_value
    mock_service_instance.executar.side_effect = Exception("Erro processamento")

    try:
        task_processar_metricas_todas_ativas()
    except Exception as e:
        assert str(e) == "Erro processamento"
