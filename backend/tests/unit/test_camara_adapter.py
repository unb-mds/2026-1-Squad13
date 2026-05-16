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

        assert proposicao is None


def test_camara_adapter_buscar_tramitacoes_brutas_sucesso(adapter):
    mock_dados = {
        "dados": [
            {
                "dataHora": "2024-01-01T10:00:00",
                "sequencia": 1,
                "siglaOrgao": "MESA",
                "descricaoTramitacao": "Apresentação",
                "despacho": ""
            },
            {
                "dataHora": "2024-01-02T10:00:00",
                "sequencia": 2,
                "siglaOrgao": "CCJ",
                "descricaoTramitacao": "Despacho",
                "despacho": "Às comissões"
            }
        ]
    }

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_dados
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Act
        tramitacoes = adapter.buscar_tramitacoes_brutas(123)

        # Assert
        assert len(tramitacoes) == 2
        assert tramitacoes[0]["descricao"] == "Apresentação"
        assert tramitacoes[0]["sigla_orgao"] == "MESA"
        assert tramitacoes[1]["descricao"] == "Despacho - Às comissões"
        assert tramitacoes[1]["sigla_orgao"] == "CCJ"
        assert tramitacoes[1]["payload_bruto"] == mock_dados["dados"][1]


def test_camara_adapter_buscar_tramitacoes_brutas_erro(adapter):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Erro")

        # Act
        tramitacoes = adapter.buscar_tramitacoes_brutas(123)

        # Assert
        assert tramitacoes == []

