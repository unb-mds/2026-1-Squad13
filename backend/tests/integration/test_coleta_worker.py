import pytest
from unittest.mock import patch, AsyncMock
from infrastructure.workers.coleta_worker import _coletar_e_salvar
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
@patch("infrastructure.workers.coleta_worker.SQLProposicaoRepository")
@patch("infrastructure.workers.coleta_worker.Session")
@patch("infrastructure.workers.coleta_worker.SenadoAdapter")
@patch("infrastructure.workers.coleta_worker.CamaraAdapter")
async def test_worker_falha_total(mock_camara, mock_senado, mock_session, mock_repo):
    """Cenário 1: Falha total de API. Ambas as fontes caem."""
    camara_instance = mock_camara.return_value
    camara_instance.coletar_em_lote = AsyncMock(side_effect=Exception("Erro Servidor Câmara"))
    
    senado_instance = mock_senado.return_value
    senado_instance.coletar_em_lote = AsyncMock(side_effect=Exception("Erro Servidor Senado"))
    
    resumo = await _coletar_e_salvar()
    
    assert resumo["camara"]["status"] == "falha"
    assert "Erro Servidor Câmara" in resumo["camara"]["erro"]
    assert resumo["senado"]["status"] == "falha"
    assert "Erro Servidor Senado" in resumo["senado"]["erro"]

@pytest.mark.asyncio
@patch("infrastructure.workers.coleta_worker.SQLProposicaoRepository")
@patch("infrastructure.workers.coleta_worker.Session")
@patch("infrastructure.workers.coleta_worker.SenadoAdapter")
@patch("infrastructure.workers.coleta_worker.CamaraAdapter")
async def test_worker_falha_parcial(mock_camara, mock_senado, mock_session, mock_repo, mock_proposicao):
    """Cenário 2: Falha parcial. Só a Câmara cai, o Senado prossegue."""
    camara_instance = mock_camara.return_value
    camara_instance.coletar_em_lote = AsyncMock(side_effect=Exception("Erro 502 Bad Gateway"))
    
    senado_instance = mock_senado.return_value
    senado_instance.coletar_em_lote = AsyncMock(return_value=[mock_proposicao])
    
    resumo = await _coletar_e_salvar()
    
    assert resumo["camara"]["status"] == "falha"
    assert resumo["senado"]["status"] == "sucesso"
    assert resumo["senado"]["itens_coletados"] == 1
    
    # Verifica se o método de persistência (que trata a idempotência) foi chamado com os dados do Senado
    repo_instance = mock_repo.return_value
    repo_instance.upsert_em_lote_por_numero_canonico.assert_called_once_with([mock_proposicao])

@pytest.mark.asyncio
@patch("infrastructure.workers.coleta_worker.SQLProposicaoRepository")
@patch("infrastructure.workers.coleta_worker.Session")
@patch("infrastructure.workers.coleta_worker.SenadoAdapter")
@patch("infrastructure.workers.coleta_worker.CamaraAdapter")
async def test_worker_upsert_sem_duplicatas(mock_camara, mock_senado, mock_session, mock_repo, mock_proposicao):
    """Cenário 3: Sucesso de fontes validando envio dos dados para repositório (Upsert sem duplicatas)."""
    camara_instance = mock_camara.return_value
    camara_instance.coletar_em_lote = AsyncMock(return_value=[mock_proposicao, mock_proposicao])
    
    senado_instance = mock_senado.return_value
    senado_instance.coletar_em_lote = AsyncMock(return_value=[mock_proposicao])
    
    resumo = await _coletar_e_salvar()
    
    assert resumo["camara"]["status"] == "sucesso"
    assert resumo["senado"]["status"] == "sucesso"
    assert resumo["camara"]["itens_coletados"] == 2
    assert resumo["senado"]["itens_coletados"] == 1
    
    repo_instance = mock_repo.return_value
    assert repo_instance.upsert_em_lote_por_numero_canonico.call_count == 2
