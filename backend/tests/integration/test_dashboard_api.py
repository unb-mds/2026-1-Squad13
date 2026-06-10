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


def test_dashboard_tempo_por_fase_sem_filtros(http_client):
    response = http_client.get("/dashboard/tempo-por-fase")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        first = data[0]
        assert "fase" in first
        assert "codigoFase" in first
        assert "tempoMedioDias" in first
        assert "quantidadeProposicoes" in first


def test_dashboard_tempo_por_fase_com_filtro_tipo(http_client):
    response = http_client.get("/dashboard/tempo-por-fase?tipo=PL")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_dashboard_tempo_por_fase_com_filtro_inexistente(http_client):
    response = http_client.get("/dashboard/tempo-por-fase?busca=TermoInexistente")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_dashboard_estoque_fases(http_client):
    response = http_client.get("/dashboard/estoque")
    assert response.status_code == 200
    data = response.json()
    assert "ativo" in data
    assert "passivo" in data
    assert isinstance(data["ativo"], list)
    assert isinstance(data["passivo"], list)


def test_dashboard_handoff(http_client):
    response = http_client.get("/dashboard/handoff")
    assert response.status_code == 200
    data = response.json()
    assert "totalEmTransito" in data
    assert "medianaDiasTransito" in data


def test_dashboard_cobertura(http_client):
    response = http_client.get("/dashboard/cobertura")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_dashboard_qualidade(http_client):
    response = http_client.get("/dashboard/qualidade")
    assert response.status_code == 200
    data = response.json()
    assert "completudePorcentagem" in data
    assert "totalProposicoes" in data
    assert "camposAnalisados" in data
