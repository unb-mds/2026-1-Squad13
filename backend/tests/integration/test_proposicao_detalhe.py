import pytest
from fastapi.testclient import TestClient
from main import app
from infrastructure.database import get_session
from sqlmodel import Session

@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    def get_session_override():
        return db_session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_obter_detalhe_proposicao_real_camara(client: TestClient):
    # ID real da Câmara (PL 21/2020)
    id_camara = "2236353"
    
    response = client.get(f"/proposicoes/{id_camara}")
    
    assert response.status_code == 200
    dados = response.json()
    assert dados["id"] == id_camara
    assert "MCN" in dados["tipo"] or "PL" in dados["tipo"] # Depende do ID, 2236353 é MCN
    assert dados["orgaoOrigem"] == "Câmara dos Deputados"
    assert "tempoTotalDias" in dados
    assert dados["tempoTotalDias"] > 0

def test_obter_detalhe_proposicao_real_senado(client: TestClient):
    # ID real do Senado (PL 21/2020 no Senado)
    id_senado = "8147067"
    
    response = client.get(f"/proposicoes/{id_senado}")
    
    assert response.status_code == 200
    dados = response.json()
    assert dados["id"] == id_senado
    assert dados["orgaoOrigem"] == "Senado Federal"
    assert dados["dataUltimaMovimentacao"] != ""
    assert "tempoTotalDias" in dados
    assert dados["tempoTotalDias"] > 0

def test_obter_detalhe_proposicao_inexistente(client: TestClient):
    response = client.get("/proposicoes/999999999")
    assert response.status_code == 404
