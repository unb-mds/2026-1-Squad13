import pytest
import requests
from unittest.mock import MagicMock, patch
from infrastructure.adapters.senado_adapter import SenadoAdapter

@pytest.fixture
def adapter():
    return SenadoAdapter()

def test_senado_adapter_normalizacao_sucesso(adapter):
    # Mock da resposta da API do Senado
    mock_dados = {
        "identificacao": "PL 456/2023",
        "autoriaIniciativa": [
            {"autor": "Senador Exemplo"}
        ],
        "documento": {
            "ementa": "Ementa de teste Senado",
            "dataApresentacao": "2023-01-01"
        },
        "autuacoes": [
            {
                "situacoes": [
                    {"descricao": "Em tramitação"}
                ]
            }
        ]
    }

    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_dados
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Act
        proposicao = adapter.buscar_por_id(54321)

        # Assert
        assert proposicao is not None
        assert proposicao.tipo == "PL"
        assert proposicao.numero == "456"
        assert proposicao.ano == 2023
        assert proposicao.autor == "Senador Exemplo"
        assert proposicao.status == "Em tramitação"
        assert proposicao.data_apresentacao == "2023-01-01"
        assert proposicao.data_ultima_movimentacao == "2023-01-01" # No mock, inicio is missing but fallback should work if I add it

def test_senado_adapter_data_ultima_movimentacao_sucesso(adapter):
    mock_dados = {
        "identificacao": "PL 456/2023",
        "documento": {"dataApresentacao": "2023-01-01"},
        "autuacoes": [
            {
                "situacoes": [
                    {"descricao": "Status Antigo", "inicio": "2023-01-01"},
                    {"descricao": "Status Novo", "inicio": "2023-02-01"}
                ]
            }
        ]
    }

    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_dados
        mock_get.return_value = mock_response

        proposicao = adapter.buscar_por_id(54321)

        assert proposicao.status == "Status Novo"
        assert proposicao.data_ultima_movimentacao == "2023-02-01"

def test_senado_adapter_fallback_data_ultima_movimentacao(adapter):
    mock_dados = {
        "identificacao": "PL 456/2023",
        "documento": {"dataApresentacao": "2023-01-01"},
        "autuacoes": []
    }

    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_dados
        mock_get.return_value = mock_response

        proposicao = adapter.buscar_por_id(54321)

        assert proposicao.data_ultima_movimentacao == "2023-01-01"

def test_senado_adapter_erro_rede(adapter):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Erro de conexão")
        
        # Act
        proposicao = adapter.buscar_por_id(54321)
        
        # Assert
        assert proposicao is None

def test_senado_adapter_buscar_tramitacoes_sucesso(adapter):
    mock_dados = {
        "autuacoes": [
            {
                "situacoes": [
                    {"descricao": "Status 1", "inicio": "2024-05-11T10:00:00"},
                    {"descricao": "Status 2", "inicio": "2024-05-12T10:00:00"}
                ]
            }
        ]
    }

    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_dados
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        tramitacoes = adapter.buscar_tramitacoes(54321)

        assert len(tramitacoes) == 2
        # Ordenação descendente no adapter: Status 2 deve vir primeiro
        assert tramitacoes[0].status == "Status 2"
        assert tramitacoes[1].status == "Status 1"

def test_senado_adapter_buscar_tramitacoes_erro(adapter):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Erro genérico")
        
        tramitacoes = adapter.buscar_tramitacoes(54321)
        
        assert tramitacoes == []

def test_senado_adapter_erro_inesperado_buscar_por_id(adapter):
    with patch('requests.get') as mock_get:
        # Força um erro ao tentar acessar o JSON
        mock_response = MagicMock()
        mock_response.json.side_effect = Exception("Erro ao processar JSON")
        mock_get.return_value = mock_response
        
        proposicao = adapter.buscar_por_id(54321)
        
        assert proposicao is None
