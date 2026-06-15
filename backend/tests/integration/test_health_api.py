from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from infrastructure.database import get_session
from main import app

client = TestClient(app)


@pytest.fixture
def mock_db_session():
    """Cria um mock para a sessão do banco de dados."""
    session = MagicMock()
    return session


def test_health_success(mock_db_session):
    """Valida retorno 200 quando todas as dependências estão OK."""
    # Override da dependência do FastAPI
    app.dependency_overrides[get_session] = lambda: mock_db_session

    with (
        patch(
            "presentation.controllers.health_controller.get_redis_client"
        ) as mock_redis,
        patch(
            "presentation.controllers.health_controller.check_api_connectivity"
        ) as mock_api,
    ):
        mock_redis.return_value.ping.return_value = True
        mock_api.return_value = True

        response = client.get("/health")

        # Limpa override após o teste
        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["components"]["database"]["status"] == "ok"


def test_health_database_error(mock_db_session):
    """Valida retorno 503 quando o banco de dados falha."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    with (
        patch(
            "presentation.controllers.health_controller.get_redis_client"
        ) as mock_redis,
        patch(
            "presentation.controllers.health_controller.check_api_connectivity"
        ) as mock_api,
    ):
        mock_redis.return_value.ping.return_value = True
        mock_api.return_value = True

        # Forçamos erro no mock da sessão
        mock_db_session.exec.side_effect = Exception("DB Connection Failed")

        response = client.get("/health")
        app.dependency_overrides.clear()

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert data["components"]["database"]["status"] == "error"


def test_health_redis_error(mock_db_session):
    """Valida retorno 503 quando o Redis falha."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    with (
        patch(
            "presentation.controllers.health_controller.get_redis_client"
        ) as mock_redis,
        patch(
            "presentation.controllers.health_controller.check_api_connectivity"
        ) as mock_api,
    ):
        # Redis falha
        mock_redis.return_value.ping.side_effect = Exception("Redis Down")
        mock_api.return_value = True

        response = client.get("/health")
        app.dependency_overrides.clear()

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert data["components"]["redis"]["status"] == "error"


def test_health_api_degraded(mock_db_session):
    """Valida retorno 200 mas status degraded quando APIs falham."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    with (
        patch(
            "presentation.controllers.health_controller.get_redis_client"
        ) as mock_redis,
        patch(
            "presentation.controllers.health_controller.check_api_connectivity"
        ) as mock_api,
    ):
        mock_redis.return_value.ping.return_value = True

        # Simula falha apenas na API da Câmara
        def side_effect(url, **kwargs):
            return "senado" in url

        mock_api.side_effect = side_effect

        response = client.get("/health")
        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["components"]["camara_api"]["status"] == "degraded"
        assert data["components"]["senado_api"]["status"] == "ok"


def test_health_coleta_batch_success(mock_db_session):
    """Valida retorno ok no health check quando a coleta diária rodou com sucesso."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    with (
        patch(
            "presentation.controllers.health_controller.get_redis_client"
        ) as mock_redis,
        patch(
            "presentation.controllers.health_controller.check_api_connectivity"
        ) as mock_api,
        patch(
            "presentation.controllers.health_controller.SQLAuditoriaColetaRepository"
        ) as mock_auditoria,
    ):
        mock_redis.return_value.ping.return_value = True
        mock_api.return_value = True

        mock_exec = MagicMock()
        mock_exec.status = "sucesso"
        mock_exec.data_inicio.isoformat.return_value = "2026-06-11T12:00:00"
        mock_auditoria.return_value.obter_ultima_execucao.return_value = mock_exec
        mock_db_session.exec.return_value.all.return_value = [mock_exec]

        response = client.get("/health")
        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["components"]["coleta_batch"]["status"] == "ok"


def test_health_coleta_batch_falha_consecutiva(mock_db_session):
    """Valida retorno degraded no health check quando a coleta falha consecutivamente."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    with (
        patch(
            "presentation.controllers.health_controller.get_redis_client"
        ) as mock_redis,
        patch(
            "presentation.controllers.health_controller.check_api_connectivity"
        ) as mock_api,
        patch(
            "presentation.controllers.health_controller.SQLAuditoriaColetaRepository"
        ) as mock_auditoria,
    ):
        mock_redis.return_value.ping.return_value = True
        mock_api.return_value = True

        mock_exec_falha = MagicMock()
        mock_exec_falha.status = "falha"
        mock_exec_falha.data_inicio.isoformat.return_value = "2026-06-11T12:00:00"

        mock_auditoria.return_value.obter_ultima_execucao.return_value = mock_exec_falha
        mock_db_session.exec.return_value.all.return_value = [
            mock_exec_falha,
            mock_exec_falha,
            mock_exec_falha,
        ]

        response = client.get("/health")
        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["components"]["coleta_batch"]["status"] == "error"
