from datetime import datetime
from unittest.mock import MagicMock

import pytest

from application.services.obter_confiabilidade_service import ObterConfiabilidadeService
from domain.entities.proposicao import Proposicao


@pytest.fixture
def mock_proposicao_repo():
    repo = MagicMock()
    # Evita que a busca secundária retorne mocks em vez de None por padrão
    repo.buscar_por_codigo.return_value = None
    return repo


@pytest.fixture
def mock_evento_repo():
    return MagicMock()


@pytest.fixture
def service(mock_proposicao_repo, mock_evento_repo):
    return ObterConfiabilidadeService(mock_proposicao_repo, mock_evento_repo)


@pytest.mark.asyncio
async def test_obter_confiabilidade_proposicao_nao_encontrada(
    service, mock_proposicao_repo
):
    mock_proposicao_repo.buscar_por_id.return_value = None
    with pytest.raises(ValueError) as exc_info:
        await service.executar("PL-123-2024")
    assert "não encontrada" in str(exc_info.value)


@pytest.mark.asyncio
async def test_obter_confiabilidade_proposicao_encontrada_por_codigo(
    service, mock_proposicao_repo, mock_evento_repo
):
    mock_proposicao_repo.buscar_por_id.return_value = None
    proposicao = Proposicao(
        id="senado:999",
        tipo="PL",
        numero="123",
        ano=2024,
        autor="Autor Exemplo",
        ementa="Ementa exemplo",
        orgao_origem="Senado Federal",
        status="Em tramitação",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-02T10:00:00",
        link_oficial="http://link",
        regime_tramitacao="Ordinária",
    )
    mock_proposicao_repo.buscar_por_codigo.return_value = proposicao
    mock_evento_repo.buscar_por_proposicao.return_value = []

    res = await service.executar("PL-123-2024")
    assert res["cobertura"] >= 70
    mock_proposicao_repo.buscar_por_codigo.assert_called_once_with("PL", "123", 2024)


@pytest.mark.asyncio
async def test_obter_confiabilidade_proposicao_encontrada_por_codigo_invalido(
    service, mock_proposicao_repo
):
    mock_proposicao_repo.buscar_por_id.return_value = None
    with pytest.raises(ValueError):
        await service.executar("PL-abc-2024")


@pytest.mark.asyncio
async def test_obter_confiabilidade_alta_com_tags_e_eventos(
    service, mock_proposicao_repo, mock_evento_repo
):
    proposicao = Proposicao(
        id="camara:123",
        tipo="PL",
        numero="123",
        ano=2024,
        ementa="Ementa",
        autor="Autor",
        orgao_origem="Câmara dos Deputados",
        status="Status",
        orgao_atual="Orgao",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-02",
        link_oficial="http://link",
        regime_tramitacao="Regime",
        tags=["teste", "cobertura"],
        data_calculo_metricas=datetime(2024, 6, 24, 12, 0),
    )
    mock_proposicao_repo.buscar_por_id.return_value = proposicao
    mock_evento_repo.buscar_por_proposicao.return_value = [{"id": 1}]

    res = await service.executar("camara:123")
    assert res["cobertura"] == 100
    assert res["confiabilidade"] == "alta"
    assert res["statusHistorico"] == "completo"
    assert res["ultimaAtualizacao"] == "24/06/2024 às 12:00"
    assert "Câmara dos Deputados (API v2)" in res["fontes"]
    assert (
        "O histórico de eventos não pôde ser recuperado da API de origem"
        not in res["limitacoes"]
    )


@pytest.mark.asyncio
async def test_obter_confiabilidade_media_sem_tags_e_sem_eventos(
    service, mock_proposicao_repo, mock_evento_repo
):
    proposicao = Proposicao(
        id="senado:123",
        tipo="PL",
        numero="123",
        ano=2024,
        ementa="Ementa",
        autor="Autor",
        orgao_origem="Senado Federal",
        status="Status",
        orgao_atual="Orgao",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-02T10:00:00Z",
        link_oficial="http://link",
        regime_tramitacao="Regime",
        tags=[],
    )
    mock_proposicao_repo.buscar_por_id.return_value = proposicao
    mock_evento_repo.buscar_por_proposicao.return_value = []

    res = await service.executar("senado:123")
    assert res["cobertura"] == 95  # 12 campos preenchidos = 70 + 25 = 95
    assert res["confiabilidade"] == "alta"
    assert res["statusHistorico"] == "parcial"
    assert res["ultimaAtualizacao"] == "02/01/2024 às 10:00"
    assert "Senado Federal (API Dados Abertos)" in res["fontes"]
    assert (
        "O histórico de eventos não pôde ser recuperado da API de origem"
        in res["limitacoes"]
    )


@pytest.mark.asyncio
async def test_obter_confiabilidade_baixa_campos_faltantes(
    service, mock_proposicao_repo, mock_evento_repo
):
    # Proposição com muitos campos nulos para forçar cobertura baixa
    proposicao = Proposicao(
        id="camara:123",
        tipo="PL",
        numero="123",
        ano=2024,
        ementa=None,
        autor=None,
        orgao_origem=None,
        status=None,
        orgao_atual=None,
        data_apresentacao=None,
        data_ultima_movimentacao="data-invalida",
        link_oficial=None,
        regime_tramitacao=None,
    )
    mock_proposicao_repo.buscar_por_id.return_value = proposicao
    mock_evento_repo.buscar_por_proposicao.return_value = []

    res = await service.executar("camara:123")
    assert res["cobertura"] == 78
    assert res["confiabilidade"] == "media"


@pytest.mark.asyncio
async def test_obter_confiabilidade_cobertura_baixa_extrema(
    service, mock_proposicao_repo, mock_evento_repo
):
    # Proposição com o mínimo de campos
    proposicao = Proposicao(
        id="camara:123",
        tipo=None,
        numero=None,
        ano=None,
        ementa=None,
        autor=None,
        orgao_origem=None,
        status=None,
        orgao_atual=None,
        data_apresentacao=None,
        data_ultima_movimentacao=None,
        link_oficial=None,
        regime_tramitacao=None,
    )
    mock_proposicao_repo.buscar_por_id.return_value = proposicao
    mock_evento_repo.buscar_por_proposicao.return_value = []

    res = await service.executar("camara:123")
    # 0 campos preenchidos = 0/12 = 0.0 -> cobertura = 70
    assert res["cobertura"] == 70
    assert res["confiabilidade"] == "media"


@pytest.mark.asyncio
async def test_obter_confiabilidade_id_hifen_tamanho_errado(
    service, mock_proposicao_repo
):
    mock_proposicao_repo.buscar_por_id.return_value = None
    with pytest.raises(ValueError):
        await service.executar("PL-123")


@pytest.mark.asyncio
async def test_obter_confiabilidade_id_hifen_ano_invalido(
    service, mock_proposicao_repo
):
    mock_proposicao_repo.buscar_por_id.return_value = None
    with pytest.raises(ValueError):
        await service.executar("PL-123-abc")


@pytest.mark.asyncio
async def test_obter_confiabilidade_id_sem_hifen_nao_encontrado(
    service, mock_proposicao_repo
):
    mock_proposicao_repo.buscar_por_id.return_value = None
    with pytest.raises(ValueError):
        await service.executar("12345")
