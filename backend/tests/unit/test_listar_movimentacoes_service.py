import pytest
from unittest.mock import Mock, MagicMock, patch
from application.services.listar_movimentacoes_service import ListarMovimentacoesService
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.tipo_evento import TipoEvento


@pytest.fixture
def mocks():
    return {
        "evento_repo": MagicMock(),
        "proposicao_repo": MagicMock(),
        "fase_repo": MagicMock(),
        "orgao_repo": MagicMock(),
        "camara_adapter": MagicMock(),
        "senado_adapter": MagicMock(),
    }


@pytest.fixture
def service(mocks):
    return ListarMovimentacoesService(
        evento_repo=mocks["evento_repo"],
        proposicao_repo=mocks["proposicao_repo"],
        fase_repo=mocks["fase_repo"],
        orgao_repo=mocks["orgao_repo"],
        camara_adapter=mocks["camara_adapter"],
        senado_adapter=mocks["senado_adapter"],
    )


def test_listar_retorna_do_cache_se_existir(service, mocks):
    # Arrange
    evento_mock = EventoTramitacao(
        proposicao_id="123",
        data_evento="2024-01-01",
        sequencia=1,
        sigla_orgao="CCJ",
        descricao_original="Teste",
        tipo_evento=TipoEvento.DESPACHO.value,
        deliberativo=False,
        mudou_fase=False,
        mudou_orgao=False,
    )
    mocks["evento_repo"].buscar_por_proposicao.return_value = [evento_mock]

    # Act
    resultado = service.executar("123")

    # Assert
    assert resultado == [evento_mock]
    mocks["camara_adapter"].buscar_tramitacoes_brutas.assert_not_called()
    mocks["senado_adapter"].buscar_tramitacoes_brutas.assert_not_called()


@patch("application.services.listar_movimentacoes_service.NormalizarTramitacaoService")
def test_listar_busca_api_camara_salva_no_cache(MockNormalizar, service, mocks):
    # Arrange
    mocks["evento_repo"].buscar_por_proposicao.return_value = []

    prop_mock = Mock()
    prop_mock.orgao_origem = "Câmara dos Deputados"
    mocks["proposicao_repo"].buscar_por_id.return_value = prop_mock

    dados_brutos = [{"descricao": "Teste"}]
    mocks["camara_adapter"].buscar_tramitacoes_brutas.return_value = dados_brutos

    evento_normalizado = EventoTramitacao(
        proposicao_id="123",
        data_evento="2024-01-01",
        sequencia=1,
        sigla_orgao="CCJ",
        descricao_original="Teste",
        tipo_evento=TipoEvento.DESPACHO.value,
        deliberativo=False,
        mudou_fase=False,
        mudou_orgao=False,
    )
    mock_normalizer_instance = MockNormalizar.return_value
    mock_normalizer_instance.normalizar.return_value = [evento_normalizado]

    # Act
    resultado = service.executar("123")

    # Assert
    assert resultado == [evento_normalizado]
    mocks["camara_adapter"].buscar_tramitacoes_brutas.assert_called_once_with(123)
    mocks["senado_adapter"].buscar_tramitacoes_brutas.assert_not_called()

    mock_normalizer_instance.normalizar.assert_called_once_with("123", dados_brutos)
    mocks["evento_repo"].salvar_lote.assert_called_once_with([evento_normalizado])


def test_listar_fallback_senado_sem_proposicao_no_banco(service, mocks):
    # Arrange
    mocks["evento_repo"].buscar_por_proposicao.return_value = []
    mocks["proposicao_repo"].buscar_por_id.return_value = None

    mocks["camara_adapter"].buscar_tramitacoes_brutas.return_value = []
    mocks["senado_adapter"].buscar_tramitacoes_brutas.return_value = [
        {"descricao": "Teste"}
    ]

    # Act
    with patch(
        "application.services.listar_movimentacoes_service.NormalizarTramitacaoService"
    ) as MockNormalizar:
        mock_normalizer_instance = MockNormalizar.return_value
        evento_mock = EventoTramitacao(
            proposicao_id="123",
            data_evento="2024-01-01",
            sequencia=1,
            sigla_orgao="CCJ",
            descricao_original="Teste",
            tipo_evento=TipoEvento.DESPACHO.value,
            deliberativo=False,
            mudou_fase=False,
            mudou_orgao=False,
        )
        mock_normalizer_instance.normalizar.return_value = [evento_mock]
        resultado = service.executar("123")

    # Assert
    assert resultado == [evento_mock]
    mocks["camara_adapter"].buscar_tramitacoes_brutas.assert_called_once_with(123)
    mocks["senado_adapter"].buscar_tramitacoes_brutas.assert_called_once_with(123)


def test_resolucao_slug_pl(service, mocks):
    # Arrange
    mocks["evento_repo"].buscar_por_proposicao.return_value = []

    prop_mock = Mock()
    prop_mock.id = "999"
    prop_mock.orgao_origem = "Câmara dos Deputados"

    mocks["proposicao_repo"].buscar_por_codigo.return_value = prop_mock
    mocks["proposicao_repo"].buscar_por_id.return_value = prop_mock

    mocks["camara_adapter"].buscar_tramitacoes_brutas.return_value = []

    # Act
    service.executar("PL-1-2024")

    # Assert
    mocks["proposicao_repo"].buscar_por_codigo.assert_called_once_with("PL", "1", 2024)
    # Even if it returns empty, it should have tried with "999"
    mocks["evento_repo"].buscar_por_proposicao.assert_called_once_with("999")
