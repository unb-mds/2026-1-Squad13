import pytest

@pytest.mark.integration
def test_camara_api_saude(http_client):
    """Exemplo de teste de integração real (opcional)."""
    response = http_client.get("https://dadosabertos.camara.leg.br/api/v2/proposicoes?itens=1")
    assert response.status_code == 200
