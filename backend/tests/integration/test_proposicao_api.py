
def test_health_check(http_client):
    # Act
    response = http_client.get("/health")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"

def test_buscar_proposicoes_sem_filtros_deve_retornar_400(http_client):
    # Act
    response = http_client.get("/proposicoes")
    
    # Assert
    assert response.status_code == 400
    assert "Preencha pelo menos um filtro" in response.json()["detail"]

def test_buscar_proposicoes_com_filtro_valido(http_client):
    # Act
    response = http_client.get("/proposicoes?tipo=PL")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
    assert data["items"][0]["tipo"] == "PL"

def test_buscar_proposicoes_paginacao(http_client):
    # Act
    response = http_client.get("/proposicoes?tipo=PL&pagina=1&itens_por_pagina=1")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 1
    assert data["pagina"] == 1

def test_buscar_proposicoes_sem_resultados(http_client):
    # Act
    response = http_client.get("/proposicoes?tipo=NONEXISTENT")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
