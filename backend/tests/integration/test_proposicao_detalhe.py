from unittest.mock import patch
from fastapi.testclient import TestClient
from domain.entities.proposicao import Proposicao


def _proposicao_camara() -> Proposicao:
    return Proposicao(
        id="2236353",
        tipo="PL",
        numero="21",
        ano=2020,
        autor="Autor Câmara",
        uf_autor="DF",
        orgao_origem="Câmara dos Deputados",
        status="Em tramitação",
        ementa="Ementa de teste Câmara",
        data_apresentacao="2020-02-04",
        data_ultima_movimentacao="2024-01-01",
        orgao_atual="CCJ",
        link_oficial="https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=2236353",
        tags=[],
    )


def _proposicao_senado() -> Proposicao:
    return Proposicao(
        id="8147067",
        tipo="PL",
        numero="21",
        ano=2020,
        autor="Autor Senado",
        uf_autor="N/A",
        orgao_origem="Senado Federal",
        status="Em tramitação",
        ementa="Ementa de teste Senado",
        data_apresentacao="2021-09-30",
        data_ultima_movimentacao="2024-01-01",
        orgao_atual="Senado Federal",
        link_oficial="https://wwws.senado.leg.br/ecidadania/visualizacaomateria?id=8147067",
        tags=[],
    )


def test_obterDetalheProposicao_adaptadorCamara_retorna200(http_client: TestClient):
    proposicao = _proposicao_camara()
    with patch(
        "infrastructure.adapters.camara_adapter.CamaraAdapter.buscar_por_id",
        return_value=proposicao,
    ):
        response = http_client.get("/proposicoes/2236353")

    assert response.status_code == 200
    dados = response.json()
    assert dados["id"] == "2236353"
    assert dados["codigoNormalizado"] == "PL-21-2020"
    assert dados["orgaoOrigem"] == "Câmara dos Deputados"
    assert "tempoTotalDias" in dados
    assert dados["tempoTotalDias"] > 0


def test_obterDetalheProposicao_slug_retorna200(http_client: TestClient, db_session):
    from infrastructure.repositories.sql_proposicao_repository import (
        SQLProposicaoRepository,
    )

    repo = SQLProposicaoRepository(db_session)
    proposicao = _proposicao_camara()
    repo.salvar(proposicao)

    response = http_client.get("/proposicoes/PL-21-2020")

    assert response.status_code == 200
    dados = response.json()
    assert dados["id"] == "2236353"
    assert dados["codigoNormalizado"] == "PL-21-2020"


def test_obterDetalheProposicao_adaptadorSenado_retorna200(http_client: TestClient):
    proposicao = _proposicao_senado()
    with (
        patch(
            "infrastructure.adapters.camara_adapter.CamaraAdapter.buscar_por_id",
            return_value=None,
        ),
        patch(
            "infrastructure.adapters.senado_adapter.SenadoAdapter.buscar_por_id",
            return_value=proposicao,
        ),
    ):
        response = http_client.get("/proposicoes/8147067")

    assert response.status_code == 200
    dados = response.json()
    assert dados["id"] == "8147067"
    assert dados["codigoNormalizado"] == "PL-21-2020"
    assert dados["orgaoOrigem"] == "Senado Federal"
    assert "tempoTotalDias" in dados
    assert dados["tempoTotalDias"] > 0


def test_obterDetalheProposicao_nenhumAdaptadorEncontra_retorna404(
    http_client: TestClient,
):
    with (
        patch(
            "infrastructure.adapters.camara_adapter.CamaraAdapter.buscar_por_id",
            return_value=None,
        ),
        patch(
            "infrastructure.adapters.senado_adapter.SenadoAdapter.buscar_por_id",
            return_value=None,
        ),
    ):
        response = http_client.get("/proposicoes/999999")

    assert response.status_code == 404
