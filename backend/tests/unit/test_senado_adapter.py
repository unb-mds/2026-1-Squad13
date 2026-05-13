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

def test_senado_adapter_erro_rede(adapter):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Erro de conexão")
        
        # Act
        proposicao = adapter.buscar_por_id(54321)
        
        # Assert
        assert proposicao is None
