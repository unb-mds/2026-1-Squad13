import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from application.services.coletar_em_lote_service import ColetarEmLoteService
from domain.entities.proposicao import Proposicao


@pytest.fixture
def mock_proposicao():
    return Proposicao(
        id="123",
        tipo="PL",
        numero="456",
        ano=2024,
        autor="Deputado Teste",
        uf_autor="DF",
        orgao_origem="Câmara",
        status="Em tramitação",
        ementa="Teste",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-02",
        orgao_atual="Plenário",
        link_oficial="http://teste.com",
    )


@pytest.mark.asyncio
async def test_service_falha_total(mock_proposicao):
    """Cenário 1: Falha total de API. Ambas as fontes caem."""
    mock_session = MagicMock()
    mock_camara = AsyncMock()
    mock_camara.coletar_em_lote.side_effect = Exception("Erro Câmara")
    mock_senado = AsyncMock()
    mock_senado.coletar_em_lote.side_effect = Exception("Erro Senado")

    service = ColetarEmLoteService(
        session=mock_session, camara_adapter=mock_camara, senado_adapter=mock_senado
    )

    resumo = await service.executar_coleta_diaria()

    assert resumo["camara"]["status"] == "falha"
    assert resumo["senado"]["status"] == "falha"
    # Verifica se registrou 2 logs de falha
    assert mock_session.add.call_count == 2


@pytest.mark.asyncio
async def test_service_sucesso_parcial(mock_proposicao):
    """Cenário 2: Sucesso no Senado, falha na Câmara."""
    mock_session = MagicMock()
    mock_camara = AsyncMock()
    mock_camara.coletar_em_lote.side_effect = Exception("Erro Câmara")
    mock_senado = AsyncMock()
    mock_senado.coletar_em_lote.return_value = [mock_proposicao]

    # Mock do repositório injetado internamente
    with patch(
        "application.services.coletar_em_lote_service.SQLProposicaoRepository"
    ) as MockRepo:
        repo_instance = MockRepo.return_value

        service = ColetarEmLoteService(
            session=mock_session, camara_adapter=mock_camara, senado_adapter=mock_senado
        )

        resumo = await service.executar_coleta_diaria()

        assert resumo["camara"]["status"] == "falha"
        assert resumo["senado"]["status"] == "sucesso"
        assert resumo["senado"]["itens_coletados"] == 1
        repo_instance.upsert_em_lote_por_numero_canonico.assert_called_once_with(
            [mock_proposicao]
        )


@pytest.mark.asyncio
async def test_service_sucesso_total(mock_proposicao):
    """Cenário 3: Sucesso em ambas as fontes."""
    mock_session = MagicMock()
    mock_camara = AsyncMock()
    mock_camara.coletar_em_lote.return_value = [mock_proposicao]
    mock_senado = AsyncMock()
    mock_senado.coletar_em_lote.return_value = [mock_proposicao]

    with patch(
        "application.services.coletar_em_lote_service.SQLProposicaoRepository"
    ) as MockRepo:
        repo_instance = MockRepo.return_value

        service = ColetarEmLoteService(
            session=mock_session, camara_adapter=mock_camara, senado_adapter=mock_senado
        )

        resumo = await service.executar_coleta_diaria()

        assert resumo["camara"]["status"] == "sucesso"
        assert resumo["senado"]["status"] == "sucesso"
        assert repo_instance.upsert_em_lote_por_numero_canonico.call_count == 2
