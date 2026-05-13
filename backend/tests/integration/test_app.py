from fastapi.testclient import TestClient
from main import app


def test_root_retorna_api_rodando():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API rodando"}
