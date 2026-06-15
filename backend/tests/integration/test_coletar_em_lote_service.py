from unittest.mock import AsyncMock, MagicMock

import pytest

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
    mock_repo = MagicMock()
    mock_evento_repo = MagicMock()
    mock_fase_repo = MagicMock()
    mock_orgao_repo = MagicMock()
    mock_apensamento_repo = MagicMock()
    mock_log_repo = MagicMock()

    mock_camara = AsyncMock()
    mock_camara.obter_total.side_effect = Exception("Erro Câmara")
    mock_senado = AsyncMock()
    mock_senado.obter_total.side_effect = Exception("Erro Senado")

    service = ColetarEmLoteService(
        repository=mock_repo,
        evento_repo=mock_evento_repo,
        fase_repo=mock_fase_repo,
        orgao_repo=mock_orgao_repo,
        apensamento_repo=mock_apensamento_repo,
        log_repo=mock_log_repo,
        camara_adapter=mock_camara,
        senado_adapter=mock_senado,
    )

    resumo = await service.executar_coleta_diaria()

    assert resumo["camara"]["status"] == "falha"
    assert resumo["senado"]["status"] == "falha"
    # Verifica se registrou 2 logs de falha
    assert mock_log_repo.salvar_log.call_count == 2


@pytest.mark.asyncio
async def test_service_sucesso_parcial(mock_proposicao):
    """Cenário 2: Sucesso no Senado, falha na Câmara."""
    mock_repo = MagicMock()
    # Mock do repo para simular gap apenas em PL 2026
    def contar_mock(tipo=None, ano=None, orgao_origem=None):
        if ano == 2026 and tipo == "PL":
            return 9
        return 10
    mock_repo.contar.side_effect = contar_mock

    mock_evento_repo = MagicMock()
    mock_fase_repo = MagicMock()
    mock_orgao_repo = MagicMock()
    mock_apensamento_repo = MagicMock()
    mock_log_repo = MagicMock()

    mock_camara = AsyncMock()
    mock_camara.obter_total.side_effect = Exception("Erro Câmara")

    mock_senado = AsyncMock()
    mock_senado.obter_total.return_value = 10
    # O local_offset do Senado será 9, então fornecemos lista com tamanho 10 para fatia [9:10] retornar o ID
    mock_senado.listar_recentes.return_value = [0, 1, 2, 3, 4, 5, 6, 7, 8, 456]
    mock_senado.buscar_por_id.return_value = mock_proposicao

    service = ColetarEmLoteService(
        repository=mock_repo,
        evento_repo=mock_evento_repo,
        fase_repo=mock_fase_repo,
        orgao_repo=mock_orgao_repo,
        apensamento_repo=mock_apensamento_repo,
        log_repo=mock_log_repo,
        camara_adapter=mock_camara,
        senado_adapter=mock_senado,
    )

    resumo = await service.executar_coleta_diaria()

    assert resumo["camara"]["status"] == "falha"
    assert resumo["senado"]["status"] == "sucesso"
    assert resumo["senado"]["itens_coletados"] == 1
    mock_repo.upsert_em_lote_por_numero_canonico.assert_called_once_with(
        [mock_proposicao]
    )


@pytest.mark.asyncio
async def test_service_sucesso_total(mock_proposicao):
    """Cenário 3: Sucesso em ambas as fontes."""
    mock_repo = MagicMock()
    # Mock do repo para simular gap apenas em PL 2026
    def contar_mock(tipo=None, ano=None, orgao_origem=None):
        if ano == 2026 and tipo == "PL":
            return 9
        return 10
    mock_repo.contar.side_effect = contar_mock

    mock_evento_repo = MagicMock()
    mock_fase_repo = MagicMock()
    mock_orgao_repo = MagicMock()
    mock_apensamento_repo = MagicMock()
    mock_log_repo = MagicMock()

    mock_camara = AsyncMock()
    mock_camara.obter_total.return_value = 10
    mock_camara.listar_recentes.return_value = [123]
    mock_camara.buscar_por_id.return_value = mock_proposicao

    mock_senado = AsyncMock()
    mock_senado.obter_total.return_value = 10
    mock_senado.listar_recentes.return_value = [0, 1, 2, 3, 4, 5, 6, 7, 8, 456]
    mock_senado.buscar_por_id.return_value = mock_proposicao

    service = ColetarEmLoteService(
        repository=mock_repo,
        evento_repo=mock_evento_repo,
        fase_repo=mock_fase_repo,
        orgao_repo=mock_orgao_repo,
        apensamento_repo=mock_apensamento_repo,
        log_repo=mock_log_repo,
        camara_adapter=mock_camara,
        senado_adapter=mock_senado,
    )

    resumo = await service.executar_coleta_diaria()

    assert resumo["camara"]["status"] == "sucesso"
    assert resumo["senado"]["status"] == "sucesso"
    # O total coletado deve ser 1 por fonte (Câmara e Senado)
    assert resumo["camara"]["itens_coletados"] == 1
    assert resumo["senado"]["itens_coletados"] == 1
    assert mock_repo.upsert_em_lote_por_numero_canonico.call_count == 2
