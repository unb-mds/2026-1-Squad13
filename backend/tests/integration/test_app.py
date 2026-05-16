from fastapi.testclient import TestClient
from main import app


def test_root_retorna_api_rodando():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API rodando"}


def test_health_success(http_client: TestClient):
    response = http_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_health_failure(http_client: TestClient):
    # Mock do get_session para falhar
    from infrastructure.database import get_session
    from unittest.mock import Mock

    mock_session = Mock()
    mock_session.exec.side_effect = Exception("DB error")

    def override():
        yield mock_session

    app.dependency_overrides[get_session] = override

    response = http_client.get("/health")
    assert response.json() == {"status": "error", "database": "disconnected"}

    # Limpa override
    app.dependency_overrides.clear()


def test_app_lifespan():
    # O uso do context manager 'with' dispara o lifespan
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
