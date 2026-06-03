from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from domain.entities.proposicao import Proposicao
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
    with (
        patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get,
        patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
    ):
        mock_get.side_effect = httpx.RequestError("Erro de conexão")

        # Act
        proposicao = await adapter.buscar_por_id(54321)

        # Assert
        assert proposicao is None
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2


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
        # Nota: O adapter preserva o case original da descrição
        assert tramitacoes[0]["descricao"] == "Situação Antiga"
        assert tramitacoes[0]["sigla_orgao"] == "PLEN"
        assert tramitacoes[0]["sequencia"] == 1

        assert tramitacoes[1]["descricao"] == "Situação Nova"
        assert tramitacoes[1]["sigla_orgao"] == "CCJ"
        assert tramitacoes[1]["sequencia"] == 2


@pytest.mark.asyncio
async def test_senado_adapter_buscar_tramitacoes_brutas_erro(adapter):
    with (
        patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get,
        patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
    ):
        mock_get.side_effect = httpx.RequestError("Erro")

        # Act
        tramitacoes = await adapter.buscar_tramitacoes_brutas(123)

        # Assert
        assert tramitacoes == []
        # No Senado, buscar_tramitacoes_brutas tenta buscar a materia primeiro.
        # Se falha, o erro é propagado.
        assert mock_get.call_count == 4
        assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_senado_adapter_buscar_por_id_detalhe_materia(adapter):
    """Testa o caminho onde a resposta contém DetalheMateria."""
    mock_dados = {
        "DetalheMateria": {
            "Materia": {
                "IdentificacaoMateria": {
                    "DescricaoIdentificacaoMateria": "PL 123/2024",
                },
                "DadosBasicosMateria": {
                    "EmentaMateria": "Ementa Teste",
                    "DataApresentacao": "2024-01-01",
                    "Autor": "Senador",
                },
                "SituacaoAtual": {
                    "Autuacoes": {
                        "Autuacao": {
                            "Situacao": {
                                "DescricaoSituacao": "Status",
                                "DataSituacao": "2024-02-01",
                            }
                        }
                    }
                },
            }
        }
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_dados
        mock_get.return_value = mock_response

        proposicao = await adapter.buscar_por_id(123)

        assert proposicao is not None
        assert proposicao.tipo == "PL"
        assert proposicao.numero == "123"
        assert proposicao.status == "Status"


@pytest.mark.asyncio
async def test_senado_adapter_listar_recentes(adapter):
    mock_dados = [
        {"codigoMateria": 1},
        {"codigoMateria": 2},
    ]

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_dados
        mock_get.return_value = mock_response

        ids = await adapter.listar_recentes("PL", 2)

        assert ids == [1, 2]


@pytest.mark.asyncio
async def test_senado_adapter_buscar_id_por_identificacao(adapter):
    mock_dados = [
        {"codigoMateria": 12345},
    ]

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_dados
        mock_get.return_value = mock_response

        id_encontrado = await adapter.buscar_id_por_identificacao("PL", "101", 2024)

        assert id_encontrado == 12345


@pytest.mark.asyncio
async def test_senado_adapter_coletar_em_lote_sucesso(adapter):
    mock_dados_lote = [
        {"codigoMateria": 100},
        {"codigoMateria": 200},
    ]

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_resp_lote = MagicMock()
        mock_resp_lote.status_code = 200
        mock_resp_lote.json.return_value = mock_dados_lote
        mock_get.return_value = mock_resp_lote

        # Patch buscar_por_id
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
            mock_get.assert_called_once()
