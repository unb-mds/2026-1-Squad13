from unittest.mock import patch
from fastapi.testclient import TestClient
from domain.entities.tramitacao import Tramitacao
from domain.entities.proposicao import Proposicao

def _tramitacao_mock(id_prop: str) -> Tramitacao:
    return Tramitacao(
        proposicao_id=id_prop,
        data_hora="2024-05-14T10:00:00",
        sequencia=1,
        sigla_orgao="CCJ",
        descricao_tramitacao="Recebimento na CCJ",
        status="Aguardando relator"
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
        tags=[]
    )

def test_listar_movimentacoes_camara_retorna200(http_client: TestClient):
    id_prop = "123456"
    prop = _proposicao_mock(id_prop, "Câmara dos Deputados")
    tram = _tramitacao_mock(id_prop)
    
    with patch("infrastructure.repositories.sql_proposicao_repository.SQLProposicaoRepository.buscar_por_id", return_value=prop), \
         patch("infrastructure.repositories.sql_tramitacao_repository.SQLTramitacaoRepository.buscar_por_proposicao", return_value=[]), \
         patch("infrastructure.adapters.camara_adapter.CamaraAdapter.buscar_tramitacoes", return_value=[tram]), \
         patch("infrastructure.repositories.sql_tramitacao_repository.SQLTramitacaoRepository.salvar_lote"):
        
        response = http_client.get(f"/proposicoes/{id_prop}/movimentacoes")
    
    assert response.status_code == 200
    dados = response.json()
    assert len(dados) == 1
    assert dados[0]["proposicaoId"] == id_prop
    assert dados[0]["siglaOrgao"] == "CCJ"

def test_listar_movimentacoes_senado_retorna200(http_client: TestClient):
    id_prop = "654321"
    prop = _proposicao_mock(id_prop, "Senado Federal")
    tram = _tramitacao_mock(id_prop)
    
    with patch("infrastructure.repositories.sql_proposicao_repository.SQLProposicaoRepository.buscar_por_id", return_value=prop), \
         patch("infrastructure.repositories.sql_tramitacao_repository.SQLTramitacaoRepository.buscar_por_proposicao", return_value=[]), \
         patch("infrastructure.adapters.senado_adapter.SenadoAdapter.buscar_tramitacoes", return_value=[tram]), \
         patch("infrastructure.repositories.sql_tramitacao_repository.SQLTramitacaoRepository.salvar_lote"):
        
        response = http_client.get(f"/proposicoes/{id_prop}/movimentacoes")
    
    assert response.status_code == 200
    dados = response.json()
    assert len(dados) == 1
    assert dados[0]["proposicaoId"] == id_prop

def test_listar_movimentacoes_usa_cache_do_banco(http_client: TestClient):
    id_prop = "111222"
    tram = _tramitacao_mock(id_prop)
    
    with patch("infrastructure.repositories.sql_tramitacao_repository.SQLTramitacaoRepository.buscar_por_proposicao", return_value=[tram]), \
         patch("infrastructure.repositories.sql_proposicao_repository.SQLProposicaoRepository.buscar_por_id") as mock_prop_repo:
        
        response = http_client.get(f"/proposicoes/{id_prop}/movimentacoes")
        
        # Não deve nem buscar a proposição se já tem as tramitações em cache
        mock_prop_repo.assert_not_called()
    
    assert response.status_code == 200
    assert len(response.json()) == 1
