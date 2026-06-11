from unittest.mock import MagicMock, patch

import pytest
import requests

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

    with patch.object(adapter.session, "get") as mock_get:
        # Configura as respostas sequenciais para as duas chamadas GET
        mock_response_prop = MagicMock()
        mock_response_prop.json.return_value = mock_dados_prop
        mock_response_prop.raise_for_status.return_value = None

        mock_response_autores = MagicMock()
        mock_response_autores.json.return_value = mock_dados_autores
        mock_response_autores.raise_for_status.return_value = None

        mock_response_rel = MagicMock()
        mock_response_rel.json.return_value = {"dados": [], "links": []}
        mock_response_rel.raise_for_status.return_value = None

        mock_get.side_effect = [
            mock_response_prop,
            mock_response_autores,
            mock_response_rel,
        ]

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
    with patch.object(adapter.session, "get") as mock_get:
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

    with patch.object(adapter.session, "get") as mock_get:
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
        assert tramitacoes[1]["descricao"] == "Despacho - às comissões"
        assert tramitacoes[1]["sigla_orgao"] == "CCJ"
        assert tramitacoes[1]["payload_bruto"] == mock_dados["dados"][1]


def test_camara_adapter_buscar_tramitacoes_brutas_erro(adapter):
    with patch.object(adapter.session, "get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Erro")

        # Act
        tramitacoes = adapter.buscar_tramitacoes_brutas(123)

        # Assert
        assert tramitacoes == []


def test_camara_adapter_contagem_emendas_com_paginacao(adapter):
    """
    Testa se o adaptador busca proposições relacionadas, trata paginação
    e filtra corretamente as emendas (EMP, EMC, SBT, etc).
    """
    id_prop = 2256735  # Exemplo de ID (PL 2630/2020)

    # Mock da primeira página
    mock_page1 = {
        "dados": [
            {"siglaTipo": "EMP"},  # Emenda de Plenário (Soma)
            {"siglaTipo": "EMC"},  # Emenda na Comissão (Soma)
            {"siglaTipo": "SBT"},  # Substitutivo (Soma)
            {"siglaTipo": "PL"},  # Outro tipo (Não soma)
        ],
        "links": [
            {
                "rel": "next",
                "href": "https://dadosabertos.camara.leg.br/api/v2/proposicoes/2256735/relacionadas?pagina=2",
            }
        ],
    }

    # Mock da segunda página (última)
    mock_page2 = {
        "dados": [
            {"siglaTipo": "EMD"},  # Emenda de Devolução/Outra (Soma: inicia com EM)
            {"siglaTipo": "REQ"},  # Requerimento (Não soma)
        ],
        "links": [
            {"rel": "self", "href": "...pagina=2"},
            {"rel": "first", "href": "...pagina=1"},
        ],
    }

    # Mock da proposição principal e autores (necessários para o buscar_por_id)
    mock_dados_prop = {
        "dados": {
            "siglaTipo": "PL",
            "numero": 2630,
            "ano": 2020,
            "ementa": "Fake News",
            "dataApresentacao": "2020-01-01",
            "statusProposicao": {"dataHora": "2020-01-01T10:00:00"},
        }
    }
    mock_dados_autores = {"dados": [{"nome": "Autor Teste", "siglaUf": "DF"}]}

    with patch.object(adapter.session, "get") as mock_get:
        # Configura as respostas: Prop, Autores, Relacionadas P1, Relacionadas P2
        r_prop = MagicMock()
        r_prop.json.return_value = mock_dados_prop
        r_prop.raise_for_status.return_value = None

        r_autores = MagicMock()
        r_autores.json.return_value = mock_dados_autores
        r_autores.raise_for_status.return_value = None

        r_p1 = MagicMock()
        r_p1.json.return_value = mock_page1
        r_p1.raise_for_status.return_value = None

        r_p2 = MagicMock()
        r_p2.json.return_value = mock_page2
        r_p2.raise_for_status.return_value = None

        mock_get.side_effect = [r_prop, r_autores, r_p1, r_p2]

        # Act
        proposicao = adapter.buscar_por_id(id_prop)

        # Assert
        assert proposicao is not None
        # EMP, EMC, SBT (P1) + EMD (P2) = 4 emendas
        assert hasattr(proposicao, "numero_emendas"), (
            "Entidade Proposicao deve ter campo numero_emendas"
        )
        assert proposicao.numero_emendas == 4

        # Verifica se chamou o endpoint correto
        # Chamada 1: /proposicoes/id
        # Chamada 2: /proposicoes/id/autores
        # Chamada 3: /proposicoes/id/relacionadas (P1)
        # Chamada 4: /proposicoes/id/relacionadas?pagina=2 (P2)
        assert mock_get.call_count == 4
        args_rel = mock_get.call_args_list[2][0][0]
        assert "relacionadas" in args_rel
