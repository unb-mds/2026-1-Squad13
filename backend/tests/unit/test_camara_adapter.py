import pytest
import requests
from unittest.mock import MagicMock, patch
from infrastructure.adapters.camara_adapter import CamaraAdapter


@pytest.fixture
def adapter():
    return CamaraAdapter()


def test_camara_adapter_normalizacao_sucesso(adapter):
    # Mock das respostas da API
    mock_dados_prop = {
        "dados": {
            "siglaTipo": "PL",
            "numero": 123,
            "ano": 2024,
            "ementa": "Ementa de teste",
            "dataApresentacao": "2024-05-11",
            "statusProposicao": {
                "despacho": "Aguardando Parecer",
                "dataHora": "2024-05-11T10:00:00",
                "siglaOrgao": "CCJ",
            },
        }
    }

    mock_dados_autores = {"dados": [{"nome": "Deputado Exemplo", "siglaUf": "SP"}]}

    with patch("requests.get") as mock_get:
        # Configura as respostas sequenciais para as duas chamadas GET
        mock_response_prop = MagicMock()
        mock_response_prop.json.return_value = mock_dados_prop
        mock_response_prop.raise_for_status.return_value = None

        mock_response_autores = MagicMock()
        mock_response_autores.json.return_value = mock_dados_autores
        mock_response_autores.raise_for_status.return_value = None

        mock_get.side_effect = [mock_response_prop, mock_response_autores]

        # Act
        proposicao = adapter.buscar_por_id(12345)

        # Assert
        assert proposicao is not None
        assert proposicao.tipo == "PL"
        assert proposicao.numero == "123"
        assert proposicao.autor == "Deputado Exemplo"
        assert proposicao.uf_autor == "SP"
        assert proposicao.status == "Aguardando Parecer"


def test_camara_adapter_erro_rede(adapter):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Erro de conexão")

        # Act
        proposicao = adapter.buscar_por_id(12345)

        # Assert
        assert proposicao is None
