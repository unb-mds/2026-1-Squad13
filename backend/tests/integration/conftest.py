import pytest
import httpx
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def http_client():
    """
    Cliente real para testes de integração de rede.
    Use com @pytest.mark.integration para não rodar no CI normal.
    """
    with httpx.Client(timeout=10.0) as client:
        yield client

@pytest.fixture
def client():
    """
    Fixture que fornece um cliente de teste para a API FastAPI.
    """
    return TestClient(app)
