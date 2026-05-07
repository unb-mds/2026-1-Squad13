import pytest

def test_health_check(client):
    # Act
    response = client.get("/health")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_buscar_proposicoes_sem_filtros_deve_retornar_400(client):
    # Act
    response = client.get("/proposicoes")
    
    # Assert
    assert response.status_code == 400
    assert "Preencha pelo menos um filtro" in response.json()["detail"]

def test_buscar_proposicoes_com_filtro_valido(client):
    # Act
    response = client.get("/proposicoes?tipo=PL")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] > 0
