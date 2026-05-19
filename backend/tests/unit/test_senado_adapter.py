import pytest
import httpx
from unittest.mock import MagicMock, patch, AsyncMock
from infrastructure.adapters.senado_adapter import SenadoAdapter


@pytest.fixture
def adapter():
    return SenadoAdapter()


@pytest.mark.asyncio
async def test_senado_adapter_normalizacao_sucesso(adapter):
    # Mock da resposta da API do Senado
    mock_dados = {
        "identificacao": "PL 456/2023",
        "autoriaIniciativa": [{"autor": "Senador Exemplo"}],
        "documento": {
            "ementa": "Ementa de teste Senado",
            "dataApresentacao": "2023-01-01",
        },
        "autuacoes": [
            {"situacoes": [{"descricao": "Em tramitação", "inicio": "2023-01-01"}]}
        ],
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_dados
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Act
        proposicao = await adapter.buscar_por_id(54321)

        # Assert
        assert proposicao is not None
        assert proposicao.tipo == "PL"
        assert proposicao.numero == "456"
        assert proposicao.ano == 2023
        assert proposicao.autor == "Senador Exemplo"
        assert proposicao.status == "Em tramitação"
        assert proposicao.data_apresentacao == "2023-01-01"
        assert proposicao.data_ultima_movimentacao == "2023-01-01"


@pytest.mark.asyncio
async def test_senado_adapter_data_ultima_movimentacao_sucesso(adapter):
    mock_dados = {
        "identificacao": "PL 456/2023",
        "documento": {"dataApresentacao": "2023-01-01"},
        "autuacoes": [
            {
                "situacoes": [
                    {"descricao": "Status Antigo", "inicio": "2023-01-01"},
                    {"descricao": "Status Novo", "inicio": "2023-02-01"},
                ]
            }
        ],
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_dados
        mock_get.return_value = mock_response

        proposicao = await adapter.buscar_por_id(54321)

        assert proposicao.status == "Status Novo"
        assert proposicao.data_ultima_movimentacao == "2023-02-01"


@pytest.mark.asyncio
async def test_senado_adapter_fallback_data_ultima_movimentacao(adapter):
    mock_dados = {
        "identificacao": "PL 456/2023",
        "documento": {"dataApresentacao": "2023-01-01"},
        "autuacoes": [],
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_dados
        mock_get.return_value = mock_response

        proposicao = await adapter.buscar_por_id(54321)

        assert proposicao.data_ultima_movimentacao == "2023-01-01"


@pytest.mark.asyncio
async def test_senado_adapter_erro_rede(adapter):
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Erro de conexão")

        # Act
        proposicao = await adapter.buscar_por_id(54321)

        # Assert
        assert proposicao is None


@pytest.mark.asyncio
async def test_senado_adapter_buscar_tramitacoes_brutas_sucesso(adapter):
    mock_dados_materia = {
        "DetalheMateria": {
            "Materia": {"IdentificacaoMateria": {"IdentificacaoProcesso": "999"}}
        }
    }

    mock_dados_processo = {
        "autuacoes": [
            {
                "situacoes": [
                    {
                        "inicio": "2024-01-02",
                        "colegiado": {"sigla": "CCJ"},
                        "descricao": "Situação Nova",
                    },
                    {
                        "inicio": "2024-01-01",
                        "colegiado": {"sigla": "PLEN"},
                        "descricao": "Situação Antiga",
                    },
                ]
            }
        ]
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        # Duas respostas: a primeira pra buscar id do processo, a segunda pro processo em si
        mock_resp_mat = MagicMock()
        mock_resp_mat.status_code = 200
        mock_resp_mat.json.return_value = mock_dados_materia

        mock_resp_proc = MagicMock()
        mock_resp_proc.status_code = 200
        mock_resp_proc.json.return_value = mock_dados_processo

        mock_get.side_effect = [mock_resp_mat, mock_resp_proc]

        # Act
        tramitacoes = await adapter.buscar_tramitacoes_brutas(123)

        # Assert
        assert len(tramitacoes) == 2

        # A API do Senado inverte (mais antigas ganham sequencia menor)
        assert tramitacoes[0]["descricao"] == "Situação antiga"
        assert tramitacoes[0]["sigla_orgao"] == "PLEN"
        assert tramitacoes[0]["sequencia"] == 1

        assert tramitacoes[1]["descricao"] == "Situação nova"
        assert tramitacoes[1]["sigla_orgao"] == "CCJ"
        assert tramitacoes[1]["sequencia"] == 2


@pytest.mark.asyncio
async def test_senado_adapter_buscar_tramitacoes_brutas_erro(adapter):
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Erro")

        # Act
        tramitacoes = await adapter.buscar_tramitacoes_brutas(123)

        # Assert
        assert tramitacoes == []
