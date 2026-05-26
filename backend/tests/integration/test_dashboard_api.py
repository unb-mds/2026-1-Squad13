def test_dashboard_metricas_sem_filtros(http_client):
    response = http_client.get("/dashboard/metricas")
    assert response.status_code == 200
    data = response.json()
    assert "totalProposicoes" in data
    assert "tempoMedioTramitacao" in data
    assert "iarMedio" in data
    assert "ieiMedio" in data
    assert "percentualAtrasadas" in data
    assert data["totalProposicoes"] >= 1


def test_dashboard_metricas_com_filtro_tipo(http_client):
    response = http_client.get("/dashboard/metricas?tipo=PL")
    assert response.status_code == 200
    data = response.json()
    assert data["totalProposicoes"] >= 1


def test_dashboard_metricas_com_filtro_status(http_client):
    response = http_client.get("/dashboard/metricas?status=Aprovada")
    assert response.status_code == 200
    data = response.json()
    assert "totalAprovadas" in data


def test_dashboard_metricas_com_filtro_inexistente(http_client):
    response = http_client.get("/dashboard/metricas?busca=TermoInexistente")
    assert response.status_code == 200
    data = response.json()
    assert data["totalProposicoes"] == 0
    assert data["tempoMedioTramitacao"] == 0
