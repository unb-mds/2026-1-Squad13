import pytest
from unittest.mock import Mock
from domain.entities.proposicao import Proposicao
from application.services.dashboard_service import DashboardService

@pytest.fixture
def mock_repo():
    return Mock()

def test_obter_metricas_vazio(mock_repo):
    mock_repo.filtrar.return_value = []
    service = DashboardService(mock_repo)
    
    metricas = service.obter_metricas()
    
    assert metricas["totalProposicoes"] == 0
    assert metricas["tempoMedioTramitacao"] == 0
    assert metricas["comissaoMaiorTempo"] == "N/A"

def test_obter_metricas_com_dados(mock_repo):
    p1 = Proposicao(id="1", tipo="PL", numero="1", ano=2024, status="Aprovada", 
                    data_apresentacao="2024-01-01", data_ultima_movimentacao="2024-01-01",
                    orgao_atual="CCJ", tempo_total_dias=100)
    p2 = Proposicao(id="2", tipo="PEC", numero="2", ano=2024, status="Em tramitação", 
                    data_apresentacao="2024-01-01", data_ultima_movimentacao="2024-01-01",
                    orgao_atual="CFT", tempo_total_dias=200) # Tem atraso (> 180)
    
    mock_repo.filtrar.return_value = [p1, p2]
    service = DashboardService(mock_repo)
    
    metricas = service.obter_metricas()
    
    assert metricas["totalProposicoes"] == 2
    assert metricas["totalAprovadas"] == 1
    assert metricas["totalEmTramitacao"] == 1
    assert metricas["proposicoesComAtraso"] == 1
    assert metricas["tempoMedioTramitacao"] == 150
    assert metricas["comissaoMaiorTempo"] == "CFT"
    assert metricas["comissaoMaiorTempoMedia"] == 200

def test_obter_dados_tipo(mock_repo):
    p1 = Proposicao(id="1", tipo="PL", numero="1", ano=2024, status="Sancionada", 
                    data_apresentacao="2024-01-01", data_ultima_movimentacao="2024-01-01",
                    orgao_atual="CCJ", tempo_total_dias=100)
    p2 = Proposicao(id="2", tipo="PL", numero="2", ano=2024, status="Em análise", 
                    data_apresentacao="2024-01-01", data_ultima_movimentacao="2024-01-01",
                    orgao_atual="CCJ", tempo_total_dias=200)
    p3 = Proposicao(id="3", tipo="PEC", numero="3", ano=2024, status="Arquivada", 
                    data_apresentacao="2024-01-01", data_ultima_movimentacao="2024-01-01",
                    orgao_atual="CCJ", tempo_total_dias=300)
    
    mock_repo.filtrar.return_value = [p1, p2, p3]
    service = DashboardService(mock_repo)
    
    dados = service.obter_dados_tipo()
    
    # PL deve vir primeiro (quantidade 2)
    assert dados[0]["tipo"] == "PL"
    assert dados[0]["quantidade"] == 2
    assert dados[0]["tempoMedio"] == 150
    
    assert dados[1]["tipo"] == "PEC"
    assert dados[1]["quantidade"] == 1
    assert dados[1]["tempoMedio"] == 300

def test_obter_gargalos(mock_repo):
    # CCJ: 1 proposição, 300 dias (atrasada)
    p1 = Proposicao(id="1", tipo="PL", numero="1", ano=2024, status="Em tramitação", 
                    data_apresentacao="2024-01-01", data_ultima_movimentacao="2024-01-01",
                    orgao_atual="CCJ", tempo_total_dias=300)
    # CFT: 1 proposição, 60 dias (não atrasada)
    p2 = Proposicao(id="2", tipo="PL", numero="2", ano=2024, status="Em tramitação", 
                    data_apresentacao="2024-01-01", data_ultima_movimentacao="2024-01-01",
                    orgao_atual="CFT", tempo_total_dias=60)
    
    mock_repo.filtrar.return_value = [p1, p2]
    service = DashboardService(mock_repo)
    
    gargalos = service.obter_gargalos()
    
    assert gargalos[0]["orgao"] == "CCJ"
    assert gargalos[0]["taxaAtraso"] == 100
    assert gargalos[0]["tempoMedioMeses"] == 10.0 # 300 / 30
    
    assert gargalos[1]["orgao"] == "CFT"
    assert gargalos[1]["taxaAtraso"] == 0
    assert gargalos[1]["tempoMedioMeses"] == 2.0 # 60 / 30

def test_obter_dados_comissao(mock_repo):
    p1 = Proposicao(id="1", tipo="PL", numero="1", ano=2024, status="S", 
                    data_apresentacao="D", data_ultima_movimentacao="D",
                    orgao_atual="CCJ", tempo_total_dias=100)
    p2 = Proposicao(id="2", tipo="PL", numero="2", ano=2024, status="S", 
                    data_apresentacao="D", data_ultima_movimentacao="D",
                    orgao_atual=None, tempo_total_dias=200) # Deve virar "Desconhecido"
    
    mock_repo.filtrar.return_value = [p1, p2]
    service = DashboardService(mock_repo)
    
    dados = service.obter_dados_comissao()
    
    assert len(dados) == 2
    # Ordenado por tempoMedio desc: Desconhecido (200) vem antes de CCJ (100)
    assert dados[0]["comissao"] == "Desconhecido"
    assert dados[1]["comissao"] == "CCJ"

def test_obter_dados_status(mock_repo):
    mock_repo.filtrar.return_value = []
    service = DashboardService(mock_repo)
    assert service.obter_dados_status() == []

    p1 = Proposicao(id="1", tipo="PL", numero="1", ano=2024, status="Aprovada", 
                    data_apresentacao="D", data_ultima_movimentacao="D",
                    orgao_atual="CCJ", tempo_total_dias=100)
    p2 = Proposicao(id="2", tipo="PL", numero="2", ano=2024, status="Aprovada", 
                    data_apresentacao="D", data_ultima_movimentacao="D",
                    orgao_atual="CCJ", tempo_total_dias=200)
    p3 = Proposicao(id="3", tipo="PL", numero="3", ano=2024, status="Em tramitação", 
                    data_apresentacao="D", data_ultima_movimentacao="D",
                    orgao_atual="CCJ", tempo_total_dias=300)
    
    mock_repo.filtrar.return_value = [p1, p2, p3]
    service = DashboardService(mock_repo)
    
    dados = service.obter_dados_status()
    
    assert len(dados) == 2
    # Aprovada: 2/3 = 67%
    aprovada = next(d for d in dados if d["status"] == "Aprovada")
    assert aprovada["quantidade"] == 2
    assert aprovada["percentual"] == 67
