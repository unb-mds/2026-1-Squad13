from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from domain.entities.proposicao import Proposicao
from domain.exceptions import ApiConnectionError, ApiRateLimitError, ApiServerError


@pytest.fixture
def adapter():
    from infrastructure.adapters.camara_adapter import CamaraAdapter

    return CamaraAdapter()


def create_mock_response(status_code=200, json_data=None):
    """Cria um mock de httpx.Response que não dispara warnings de corrotina."""
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = status_code
    if json_data is not None:
        mock_resp.json.return_value = json_data
    mock_resp.raise_for_status.return_value = None
    return mock_resp


@pytest.mark.asyncio
async def test_camara_adapter_buscar_por_id_sucesso(adapter):
    mock_dados = {
        "dados": {
            "id": 12345,
            "siglaTipo": "PL",
            "numero": 123,
            "ano": 2024,
            "ementa": "Ementa teste",
            "dataApresentacao": "2024-01-01T10:00",
            "statusProposicao": {
                "dataHora": "2024-01-02T10:00",
                "siglaOrgao": "CCJ",
                "despacho": "Aguardando Parecer",
            },
        }
    }
    mock_autores = {
        "dados": [{"nome": "Deputado Exemplo", "siglaUf": "SP", "siglaPartido": "PT"}]
    }
    mock_relacionadas = {"dados": []}
    mock_tramitacoes = {"dados": []}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        # Mock para as 4 chamadas: prop, autores, relacionadas, tramitacoes
        mock_get.side_effect = [
            create_mock_response(json_data=mock_dados),
            create_mock_response(json_data=mock_autores),
            create_mock_response(json_data=mock_relacionadas),
            create_mock_response(json_data=mock_tramitacoes),
        ]

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
        patch("asyncio.sleep", new_callable=AsyncMock),
    ):
        mock_get.side_effect = httpx.RequestError("Erro de conexão")

        # Act & Assert
        with pytest.raises(ApiConnectionError):
            await adapter.buscar_por_id(12345)

        # Verifica se houve retentativas (3 tentativas para cada uma das 4 requisições em paralelo)
        assert mock_get.call_count == 12


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
        mock_get.return_value = create_mock_response(json_data=mock_dados)

        tramitacoes = await adapter.buscar_tramitacoes_brutas(12345)

        assert len(tramitacoes) == 2
        assert tramitacoes[0]["sigla_orgao"] == "MESA"
        assert tramitacoes[1]["sigla_orgao"] == "CCJ"


@pytest.mark.asyncio
async def test_camara_adapter_erro_500(adapter):
    with (
        patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get,
        patch("asyncio.sleep", new_callable=AsyncMock),
    ):
        mock_get.return_value = create_mock_response(status_code=500)

        # Act & Assert
        with pytest.raises(ApiServerError):
            await adapter.buscar_por_id(12345)

        # 3 tentativas por requisição paralela
        assert mock_get.call_count == 12


@pytest.mark.asyncio
async def test_camara_adapter_rate_limit(adapter):
    with (
        patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get,
        patch("asyncio.sleep", new_callable=AsyncMock),
    ):
        mock_resp = create_mock_response(status_code=429)
        mock_resp.headers = {"Retry-After": "10"}
        mock_get.return_value = mock_resp

        # Act & Assert
        with pytest.raises(ApiRateLimitError):
            await adapter.buscar_por_id(12345)


@pytest.mark.asyncio
async def test_camara_adapter_obter_total(adapter):
    mock_resp_data = {
        "links": [
            {"rel": "last", "href": "https://url.com?pagina=50&itens=1"},
            {"rel": "self", "href": "https://url.com?pagina=1&itens=1"},
        ]
    }
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = create_mock_response(json_data=mock_resp_data)

        total = await adapter.obter_total("PL", 2024)
        assert total == 50


@pytest.mark.asyncio
async def test_camara_adapter_listar_recentes(adapter):
    mock_resp_data = {"dados": [{"id": 1}, {"id": 2}, {"id": 3}]}
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = create_mock_response(json_data=mock_resp_data)

        ids = await adapter.listar_recentes("PL", 3, 2024)
        assert ids == [1, 2, 3]


@pytest.mark.asyncio
async def test_camara_adapter_coletar_em_lote(adapter):
    # Mock para listar_recentes e buscar_por_id
    mock_lista = {"dados": [{"id": 1}, {"id": 2}], "links": []}
    mock_p1 = Proposicao(id="camara:1", tipo="PL", numero="1", ano=2024)
    mock_p2 = Proposicao(id="camara:2", tipo="PL", numero="2", ano=2024)

    with (
        patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get,
        patch.object(adapter, "buscar_por_id", new_callable=AsyncMock) as mock_buscar,
    ):
        mock_get.return_value = create_mock_response(json_data=mock_lista)
        mock_buscar.side_effect = [mock_p1, mock_p2]

        proposicoes = await adapter.coletar_em_lote({"limite_total": 2})

        assert len(proposicoes) == 2
        assert proposicoes[0].id == "camara:1"
        assert proposicoes[1].id == "camara:2"
