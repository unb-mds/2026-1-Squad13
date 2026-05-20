from fastapi.testclient import TestClient

from main import app


def test_root_retorna_api_rodando():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API rodando"}


def test_health_success(http_client: TestClient):
    from unittest.mock import patch

    with (
        patch(
            "presentation.controllers.health_controller.get_redis_client"
        ) as mock_redis,
        patch(
            "presentation.controllers.health_controller.check_api_connectivity",
            return_value=True,
        ),
    ):
        mock_redis.return_value.ping.return_value = True

        response = http_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data["components"]


def test_health_failure(http_client: TestClient):
    # Mock do get_session para falhar
    from unittest.mock import Mock, patch

    from infrastructure.database import get_session

    mock_session = Mock()
    mock_session.exec.side_effect = Exception("DB error")

    def override():
        yield mock_session

    app.dependency_overrides[get_session] = override

    with (
        patch(
            "presentation.controllers.health_controller.get_redis_client"
        ) as mock_redis,
        patch(
            "presentation.controllers.health_controller.check_api_connectivity",
            return_value=True,
        ),
    ):
        mock_redis.return_value.ping.return_value = True

        response = http_client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert data["components"]["database"]["status"] == "error"

    # Limpa override
    app.dependency_overrides.clear()


def test_app_lifespan():
    # O uso do context manager 'with' dispara o lifespan
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
