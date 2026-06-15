from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.proposicao import Proposicao
from domain.entities.tipo_evento import TipoEvento


def _evento_mock(id_prop: str) -> EventoTramitacao:
    return EventoTramitacao(
        proposicao_id=id_prop,
        data_evento="2024-05-14T10:00:00",
        sequencia=1,
        sigla_orgao="CCJ",
        descricao_original="Recebimento na CCJ",
        tipo_evento=TipoEvento.NAO_CLASSIFICADO.value,
        deliberativo=False,
        mudou_fase=False,
        mudou_orgao=False,
    )


def _proposicao_mock(id_prop: str, orgao: str) -> Proposicao:
    return Proposicao(
        id=id_prop,
        tipo="PL",
        numero="123",
        ano=2024,
        autor="Test",
        orgao_origem=orgao,
        status="Test",
        ementa="Test",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        orgao_atual="Test",
        tags=[],
    )


def test_listar_movimentacoes_camara_retorna200(http_client: TestClient):
    id_prop = "123456"
    prop = _proposicao_mock(id_prop, "Câmara dos Deputados")

    tram_bruta = {
        "data_hora": "2024-05-14T10:00:00",
        "sequencia": 1,
        "sigla_orgao": "CCJ",
        "descricao": "Recebimento na CCJ",
        "payload_bruto": {},
    }

    with (
        patch(
            "infrastructure.repositories.sql_proposicao_repository.SQLProposicaoRepository.buscar_por_id",
            return_value=prop,
        ),
        patch(
            "infrastructure.repositories.sql_evento_tramitacao_repository.SQLEventoTramitacaoRepository.buscar_por_proposicao",
            return_value=[],
        ),
        patch(
            "infrastructure.adapters.camara_adapter.CamaraAdapter.buscar_tramitacoes_brutas",
            new_callable=AsyncMock,
            return_value=[tram_bruta],
        ),
        patch(
            "infrastructure.adapters.senado_adapter.SenadoAdapter.buscar_id_por_identificacao",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "infrastructure.repositories.sql_evento_tramitacao_repository.SQLEventoTramitacaoRepository.salvar_lote"
        ),
    ):
        response = http_client.get(
            f"/proposicoes/{id_prop}/movimentacoes?modo=completo"
        )

    assert response.status_code == 200
    dados = response.json()
    assert len(dados) == 1
    assert dados[0]["proposicaoId"] == id_prop
    assert dados[0]["siglaOrgao"] == "CCJ"
    assert "tipoEvento" in dados[0]
    assert "diasNaEtapa" in dados[0]
    assert "temAtraso" in dados[0]


def test_listar_movimentacoes_senado_retorna200(http_client: TestClient):
    id_prop = "654321"
    prop = _proposicao_mock(id_prop, "Senado Federal")

    tram_bruta = {
        "data_hora": "2024-05-14T10:00:00",
        "sequencia": 1,
        "sigla_orgao": "CCJ",
        "descricao": "Recebimento na CCJ",
        "payload_bruto": {},
    }

    with (
        patch(
            "infrastructure.repositories.sql_proposicao_repository.SQLProposicaoRepository.buscar_por_id",
            return_value=prop,
        ),
        patch(
            "infrastructure.repositories.sql_evento_tramitacao_repository.SQLEventoTramitacaoRepository.buscar_por_proposicao",
            return_value=[],
        ),
        patch(
            "infrastructure.adapters.senado_adapter.SenadoAdapter.buscar_tramitacoes_brutas",
            new_callable=AsyncMock,
            return_value=[tram_bruta],
        ),
        patch(
            "infrastructure.adapters.senado_adapter.SenadoAdapter.buscar_id_por_identificacao",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "infrastructure.adapters.camara_adapter.CamaraAdapter.buscar_id_por_identificacao",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "infrastructure.repositories.sql_evento_tramitacao_repository.SQLEventoTramitacaoRepository.salvar_lote"
        ),
    ):
        response = http_client.get(
            f"/proposicoes/{id_prop}/movimentacoes?modo=completo"
        )

    assert response.status_code == 200
    dados = response.json()
    assert len(dados) == 1
    assert dados[0]["proposicaoId"] == id_prop


def test_listar_movimentacoes_usa_cache_do_banco(http_client: TestClient):
    id_prop = "111222"
    evento = _evento_mock(id_prop)

    with (
        patch(
            "infrastructure.repositories.sql_evento_tramitacao_repository.SQLEventoTramitacaoRepository.buscar_por_proposicao",
            return_value=[evento],
        ),
        patch(
            "infrastructure.repositories.sql_proposicao_repository.SQLProposicaoRepository.buscar_por_id"
        ) as mock_prop_repo,
    ):
        response = http_client.get(
            f"/proposicoes/{id_prop}/movimentacoes?modo=completo"
        )

        # Não deve nem buscar a proposição se já tem as tramitações em cache
        mock_prop_repo.assert_not_called()

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_listar_movimentacoes_modo_resumido_retorna200(http_client: TestClient):
    # Verifica que ?modo=resumido retorna 200 com estrutura de PeriodoFase.
    # Usa cache vazio → normalização real → AgregarPorFaseService com DB sem fases → lista vazia.
    id_prop = "777001"
    prop = _proposicao_mock(id_prop, "Câmara dos Deputados")

    tram_bruta = {
        "data_hora": "2024-05-14T10:00:00",
        "sequencia": 1,
        "sigla_orgao": "CCJ",
        "descricao": "Recebimento na CCJ",
        "payload_bruto": {},
    }

    with (
        patch(
            "infrastructure.repositories.sql_proposicao_repository.SQLProposicaoRepository.buscar_por_id",
            return_value=prop,
        ),
        patch(
            "infrastructure.repositories.sql_evento_tramitacao_repository.SQLEventoTramitacaoRepository.buscar_por_proposicao",
            return_value=[],
        ),
        patch(
            "infrastructure.adapters.camara_adapter.CamaraAdapter.buscar_tramitacoes_brutas",
            new_callable=AsyncMock,
            return_value=[tram_bruta],
        ),
        patch(
            "infrastructure.adapters.senado_adapter.SenadoAdapter.buscar_id_por_identificacao",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "infrastructure.repositories.sql_evento_tramitacao_repository.SQLEventoTramitacaoRepository.salvar_lote"
        ),
        patch(
            "infrastructure.repositories.sql_proposicao_repository.SQLProposicaoRepository.salvar"
        ),
    ):
        response = http_client.get(
            f"/proposicoes/{id_prop}/movimentacoes?modo=resumido"
        )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_listar_movimentacoes_modo_relevante_retorna200(http_client: TestClient):
    # Verifica que ?modo=relevante retorna apenas eventos com relevante=True.
    # Usa cache com dois eventos — um relevante, um não — e confirma filtragem.
    id_prop = "777002"

    relevante = EventoTramitacao(
        proposicao_id=id_prop,
        data_evento="2024-05-14T10:00:00",
        sequencia=1,
        sigla_orgao="CCJ",
        descricao_original="Aprovação em comissão",
        tipo_evento=TipoEvento.NAO_CLASSIFICADO.value,
        deliberativo=False,
        mudou_fase=False,
        mudou_orgao=False,
        relevante=True,
    )
    nao_relevante = EventoTramitacao(
        proposicao_id=id_prop,
        data_evento="2024-06-01T10:00:00",
        sequencia=2,
        sigla_orgao="MESA",
        descricao_original="Despacho interno",
        tipo_evento=TipoEvento.NAO_CLASSIFICADO.value,
        deliberativo=False,
        mudou_fase=False,
        mudou_orgao=False,
        relevante=False,
    )

    with patch(
        "infrastructure.repositories.sql_evento_tramitacao_repository.SQLEventoTramitacaoRepository.buscar_por_proposicao",
        return_value=[relevante, nao_relevante],
    ):
        response = http_client.get(
            f"/proposicoes/{id_prop}/movimentacoes?modo=relevante"
        )

    assert response.status_code == 200
    dados = response.json()
    assert len(dados) == 1
    assert dados[0]["proposicaoId"] == id_prop
    assert dados[0]["relevante"] is True


def test_listar_movimentacoes_default_e_resumido(http_client: TestClient):
    # Verifica que omitir ?modo= é equivalente a ?modo=resumido (default do endpoint).
    id_prop = "777003"
    prop = _proposicao_mock(id_prop, "Câmara dos Deputados")

    tram_bruta = {
        "data_hora": "2024-05-14T10:00:00",
        "sequencia": 1,
        "sigla_orgao": "CCJ",
        "descricao": "Recebimento na CCJ",
        "payload_bruto": {},
    }

    with (
        patch(
            "infrastructure.repositories.sql_proposicao_repository.SQLProposicaoRepository.buscar_por_id",
            return_value=prop,
        ),
        patch(
            "infrastructure.repositories.sql_evento_tramitacao_repository.SQLEventoTramitacaoRepository.buscar_por_proposicao",
            return_value=[],
        ),
        patch(
            "infrastructure.adapters.camara_adapter.CamaraAdapter.buscar_tramitacoes_brutas",
            new_callable=AsyncMock,
            return_value=[tram_bruta],
        ),
        patch(
            "infrastructure.adapters.senado_adapter.SenadoAdapter.buscar_id_por_identificacao",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "infrastructure.repositories.sql_evento_tramitacao_repository.SQLEventoTramitacaoRepository.salvar_lote"
        ),
        patch(
            "infrastructure.repositories.sql_proposicao_repository.SQLProposicaoRepository.salvar"
        ),
    ):
        response_default = http_client.get(f"/proposicoes/{id_prop}/movimentacoes")
        response_resumido = http_client.get(
            f"/proposicoes/{id_prop}/movimentacoes?modo=resumido"
        )

    assert response_default.status_code == 200
    assert response_resumido.status_code == 200
    # Sem ?modo= deve retornar a mesma estrutura de PeriodoFase que ?modo=resumido
    assert response_default.json() == response_resumido.json()
