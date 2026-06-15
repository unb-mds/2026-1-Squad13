from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from application.services.listar_movimentacoes_service import ListarMovimentacoesService
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.fase_analitica import FaseAnalitica
from domain.entities.tipo_evento import TipoEvento
from domain.value_objects.modo_movimentacao import ModoMovimentacao
from domain.value_objects.periodo_fase import PeriodoFase


@pytest.fixture
def mocks():
    return {
        "evento_repo": MagicMock(),
        "proposicao_repo": MagicMock(),
        "fase_repo": MagicMock(),
        "orgao_repo": MagicMock(),
        "camara_adapter": AsyncMock(),
        "senado_adapter": AsyncMock(),
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


@pytest.mark.asyncio
async def test_listar_retorna_do_cache_se_existir(service, mocks):
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
    resultado = await service.executar("123", modo=ModoMovimentacao.COMPLETO)

    # Assert
    assert resultado == [evento_mock]
    mocks["camara_adapter"].buscar_tramitacoes_brutas.assert_not_called()
    mocks["senado_adapter"].buscar_tramitacoes_brutas.assert_not_called()
    mocks["evento_repo"].buscar_por_proposicao.assert_called_with(
        "123", somente_relevantes=False
    )


@pytest.mark.asyncio
@patch("application.services.listar_movimentacoes_service.NormalizarTramitacaoService")
async def test_listar_busca_api_camara_salva_no_cache(MockNormalizar, service, mocks):
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
    resultado = await service.executar("123", modo=ModoMovimentacao.COMPLETO)

    # Assert
    assert resultado == [evento_normalizado]
    mocks["camara_adapter"].buscar_tramitacoes_brutas.assert_called_once_with(
        123, client=None
    )
    mocks["senado_adapter"].buscar_tramitacoes_brutas.assert_not_called()

    mock_normalizer_instance.normalizar.assert_called_once_with("123", dados_brutos)
    mocks["evento_repo"].salvar_lote.assert_called_once_with([evento_normalizado])


@pytest.mark.asyncio
async def test_listar_fallback_senado_sem_proposicao_no_banco(service, mocks):
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
        resultado = await service.executar("123", modo=ModoMovimentacao.COMPLETO)

    # Assert
    assert resultado == [evento_mock]
    mocks["camara_adapter"].buscar_tramitacoes_brutas.assert_called_once_with(
        123, client=None
    )
    mocks["senado_adapter"].buscar_tramitacoes_brutas.assert_called_once_with(
        123, client=None, timeout=5
    )


@pytest.mark.asyncio
async def test_resolucao_slug_pl(service, mocks):
    # Arrange
    mocks["evento_repo"].buscar_por_proposicao.return_value = []

    prop_mock = Mock()
    prop_mock.id = "999"
    prop_mock.orgao_origem = "Câmara dos Deputados"

    mocks["proposicao_repo"].buscar_por_codigo.return_value = prop_mock
    mocks["proposicao_repo"].buscar_por_id.return_value = prop_mock

    mocks["camara_adapter"].buscar_tramitacoes_brutas.return_value = []

    # Act
    await service.executar("PL-1-2024", modo=ModoMovimentacao.COMPLETO)

    # Assert
    mocks["proposicao_repo"].buscar_por_codigo.assert_called_once_with("PL", "1", 2024)
    # Even if it returns empty, it should have tried with "999"
    mocks["evento_repo"].buscar_por_proposicao.assert_called_with(
        "999", somente_relevantes=False
    )


@pytest.mark.asyncio
async def test_executar_delega_filtro_relevancia_para_repositorio(service, mocks):
    # Arrange
    evento_relevante = EventoTramitacao(
        proposicao_id="123",
        data_evento="2024-01-01",
        sequencia=1,
        sigla_orgao="CCJ",
        descricao_original="Teste",
        tipo_evento=TipoEvento.DESPACHO.value,
        relevante=True,
    )
    mocks["evento_repo"].buscar_por_proposicao.return_value = [evento_relevante]

    # Act
    resultado = await service.executar("123", modo=ModoMovimentacao.RELEVANTE)

    # Assert
    assert resultado == [evento_relevante]
    # Verifica que o repositório foi chamado com somente_relevantes=True
    mocks["evento_repo"].buscar_por_proposicao.assert_called_with(
        "123", somente_relevantes=True
    )


@pytest.mark.asyncio
async def test_executar_nao_vai_para_api_se_houver_dados_no_cache_mesmo_sem_relevantes(
    service, mocks
):
    # Arrange
    # Modo RELEVANTE, repositório retorna vazio (nenhum relevante no banco)
    mocks["evento_repo"].buscar_por_proposicao.return_value = []
    # Mas o banco TEM eventos (irrelevantes)
    mocks["evento_repo"].existe_algum_evento.return_value = True

    # Act
    resultado = await service.executar("123", modo=ModoMovimentacao.RELEVANTE)

    # Assert
    assert resultado == []
    # Não deve chamar adapters
    mocks["camara_adapter"].buscar_tramitacoes_brutas.assert_not_called()
    mocks["senado_adapter"].buscar_tramitacoes_brutas.assert_not_called()
    # Deve ter verificado existência no repositório
    mocks["evento_repo"].existe_algum_evento.assert_called_with("123")


@pytest.mark.asyncio
async def test_listar_modo_resumido_retorna_periodos_de_fase():
    # AgregarPorFaseService.__init__ chama buscar_todas - fase_repo deve ser configurado
    # ANTES de instanciar ListarMovimentacoesService.
    fase = FaseAnalitica(
        codigo="ANALISE_COMISSOES", nome="Analise em comissoes", ordem_logica=2
    )
    fase.id = 1
    fase_repo = MagicMock()
    fase_repo.buscar_todas.return_value = [fase]  # configurado ANTES do __init__
    # Proposição com tipo não unificável para usar o caminho de fallback simples
    prop = Mock()
    prop.orgao_origem = "Câmara dos Deputados"
    prop.tipo = "REC"
    prop.data_encerramento = None
    prop.numero = "1"
    prop.ano = 2024
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
        fase_analitica_id=1,
    )
    evento_repo = MagicMock()
    evento_repo.buscar_por_proposicao.return_value = []
    proposicao_repo = MagicMock()
    proposicao_repo.buscar_por_id.return_value = prop
    camara_adapter = AsyncMock()
    camara_adapter.buscar_tramitacoes_brutas.return_value = [{"descricao": "Teste"}]
    service = ListarMovimentacoesService(
        evento_repo=evento_repo,
        proposicao_repo=proposicao_repo,
        fase_repo=fase_repo,
        orgao_repo=MagicMock(),
        camara_adapter=camara_adapter,
        senado_adapter=AsyncMock(),
    )
    with patch(
        "application.services.listar_movimentacoes_service.NormalizarTramitacaoService"
    ) as MockNorm:
        MockNorm.return_value.normalizar.return_value = [evento_normalizado]
        resultado = await service.executar("123", modo=ModoMovimentacao.RESUMIDO)
    assert isinstance(resultado, list)
    assert len(resultado) == 1
    assert isinstance(resultado[0], PeriodoFase)
    assert resultado[0].fase_codigo == "ANALISE_COMISSOES"


@pytest.mark.asyncio
async def test_listar_modo_resumido_com_cache_hit_retorna_periodos_de_fase():
    # fase_repo configurado ANTES de instanciar o service (AgregarPorFaseService.__init__
    # chama buscar_todas imediatamente)
    fase = FaseAnalitica(
        codigo="ANALISE_COMISSOES", nome="Analise em comissoes", ordem_logica=2
    )
    fase.id = 1
    fase_repo = MagicMock()
    fase_repo.buscar_todas.return_value = [fase]

    prop = Mock()
    prop.data_encerramento = None

    evento_cache = EventoTramitacao(
        proposicao_id="123",
        data_evento="2024-01-01",
        sequencia=1,
        sigla_orgao="CCJ",
        descricao_original="Teste",
        tipo_evento=TipoEvento.DESPACHO.value,
        deliberativo=False,
        mudou_fase=False,
        mudou_orgao=False,
        fase_analitica_id=1,
    )

    evento_repo = MagicMock()
    evento_repo.buscar_por_proposicao.return_value = [evento_cache]  # cache hit

    proposicao_repo = MagicMock()
    proposicao_repo.buscar_por_id.return_value = prop

    camara_adapter = AsyncMock()
    senado_adapter = AsyncMock()

    service = ListarMovimentacoesService(
        evento_repo=evento_repo,
        proposicao_repo=proposicao_repo,
        fase_repo=fase_repo,
        orgao_repo=MagicMock(),
        camara_adapter=camara_adapter,
        senado_adapter=senado_adapter,
    )

    # Act
    resultado = await service.executar("123", modo=ModoMovimentacao.RESUMIDO)

    # Assert — 1. retorna list[PeriodoFase]
    assert isinstance(resultado, list)
    assert len(resultado) == 1
    assert isinstance(resultado[0], PeriodoFase)

    # Assert — 2. não chama adapters externos (cache hit não deve tocar na API)
    camara_adapter.buscar_tramitacoes_brutas.assert_not_called()
    senado_adapter.buscar_tramitacoes_brutas.assert_not_called()

    # Assert — 3. busca proposicao para montar prop_resumo (proposicao=None no cache hit)
    proposicao_repo.buscar_por_id.assert_called_once_with("123")


def test_extrair_id_numerico(service):
    assert service._extrair_id_numerico("123") == 123
    assert service._extrair_id_numerico("camara:104333") == 104333
    assert service._extrair_id_numerico("senado:5678") == 5678
    assert service._extrair_id_numerico(12345) == 12345
    assert service._extrair_id_numerico(None) == 0
    assert service._extrair_id_numerico("") == 0
    assert service._extrair_id_numerico("camara:invalido") == 0
    assert service._extrair_id_numerico("texto_puro") == 0
