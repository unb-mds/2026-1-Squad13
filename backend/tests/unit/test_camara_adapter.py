from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from domain.entities.proposicao import Proposicao
from domain.exceptions import ApiConnectionError
from infrastructure.adapters.camara_adapter import CamaraAdapter


@pytest.fixture
def adapter():
    return CamaraAdapter()


@pytest.mark.asyncio
async def test_camara_adapter_normalizacao_sucesso(adapter):
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

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        # Configura as respostas sequenciais para as duas chamadas GET
        mock_response_prop = MagicMock()
        mock_response_prop.status_code = 200
        mock_response_prop.json.return_value = mock_dados_prop
        mock_response_prop.raise_for_status.return_value = None

        mock_response_autores = MagicMock()
        mock_response_autores.status_code = 200
        mock_response_autores.json.return_value = mock_dados_autores
        mock_response_autores.raise_for_status.return_value = None

        mock_get.side_effect = [mock_response_prop, mock_response_autores]

        # Act
        proposicao = await adapter.buscar_por_id(12345)

        # Assert
        assert proposicao is not None
        assert proposicao.tipo == "PL"
        assert proposicao.numero == "123"
        assert proposicao.autor == "Deputado Exemplo"
        assert proposicao.uf_autor == "SP"
        assert proposicao.status == "Aguardando Parecer"


@pytest.mark.asyncio
async def test_camara_adapter_erro_rede(adapter):
    with (
        patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get,
        patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
    ):
        mock_get.side_effect = httpx.RequestError("Erro de conexão")

        # Act & Assert
        with pytest.raises(ApiConnectionError):
            await adapter.buscar_por_id(12345)

        # Verifica se houve retentativas (3 tentativas para cada uma das 3 requisições em paralelo)
        assert mock_get.call_count == 9
        assert mock_sleep.call_count == 6


@pytest.mark.asyncio
async def test_camara_adapter_buscar_tramitacoes_brutas_sucesso(adapter):
    mock_dados = {
        "dados": [
            {
                "dataHora": "2024-01-01T10:00:00",
                "sequencia": 1,
                "siglaOrgao": "MESA",
                "descricaoTramitacao": "Apresentação",
                "despacho": "",
            },
            {
                "dataHora": "2024-01-02T10:00:00",
                "sequencia": 2,
                "siglaOrgao": "CCJ",
                "descricaoTramitacao": "Despacho",
                "despacho": "Às comissões",
            },
        ]
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_dados
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Act
        tramitacoes = await adapter.buscar_tramitacoes_brutas(123)

        # Assert
        assert len(tramitacoes) == 2
        assert tramitacoes[0]["descricao"] == "Apresentação"
        assert tramitacoes[0]["sigla_orgao"] == "MESA"
        assert tramitacoes[1]["descricao"] == "Despacho - às comissões"
        assert tramitacoes[1]["sigla_orgao"] == "CCJ"
        assert tramitacoes[1]["payload_bruto"] == mock_dados["dados"][1]


@pytest.mark.asyncio
async def test_camara_adapter_buscar_tramitacoes_brutas_erro(adapter):
    with (
        patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get,
        patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
    ):
        mock_get.side_effect = httpx.RequestError("Erro")

        # Act
        tramitacoes = await adapter.buscar_tramitacoes_brutas(123)

        # Assert
        assert tramitacoes == []
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_camara_adapter_listar_proposicoes_id_sucesso(adapter):
    mock_dados = {
        "dados": [
            {"id": 1},
            {"id": 2},
        ]
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_dados
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Act
        ids = await adapter.listar_recentes("PL", 2024, 10)

        # Assert
        assert ids == [1, 2]
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_camara_adapter_listar_proposicoes_id_erro(adapter):
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("Erro")

        # Act
        ids = await adapter.listar_recentes("PL", 2024)

        assert ids == []


@pytest.mark.asyncio
async def test_camara_adapter_buscar_id_por_identificacao_sucesso(adapter):
    mock_dados = {
        "dados": [
            {"id": 123456},
        ]
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_dados
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Act
        id_encontrado = await adapter.buscar_id_por_identificacao("PL", "101", 2024)

        # Assert
        assert id_encontrado == 123456


@pytest.mark.asyncio
async def test_camara_adapter_buscar_id_por_identificacao_vazio(adapter):
    mock_dados = {"dados": []}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_dados
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Act
        id_encontrado = await adapter.buscar_id_por_identificacao("PL", "101", 2024)

        assert id_encontrado is None


@pytest.mark.asyncio
async def test_camara_adapter_coletar_em_lote_sucesso(adapter):
    mock_dados_lote = {
        "dados": [{"id": 100}, {"id": 200}],
        "links": [{"rel": "next", "href": "..."}],
    }
    mock_dados_lote_vazio = {"dados": [], "links": []}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_resp_lote = MagicMock()
        mock_resp_lote.status_code = 200
        mock_resp_lote.json.return_value = mock_dados_lote

        mock_resp_vazio = MagicMock()
        mock_resp_vazio.status_code = 200
        mock_resp_vazio.json.return_value = mock_dados_lote_vazio

        mock_get.side_effect = [mock_resp_lote, mock_resp_vazio]

        # Patch buscar_por_id para não fazer chamadas de rede reais
        with patch.object(
            adapter, "buscar_por_id", new_callable=AsyncMock
        ) as mock_buscar:
            mock_buscar.side_effect = [
                MagicMock(spec=Proposicao),
                MagicMock(spec=Proposicao),
            ]

            # Act
            proposicoes = await adapter.coletar_em_lote({"limite_total": 2})

            # Assert
            assert len(proposicoes) == 2
            assert (
                mock_get.call_count == 1
            )  # Processa os IDs e break porque atingiu limite
