import pytest
from unittest.mock import MagicMock
from domain.entities.proposicao import Proposicao


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """
    Mock global do Redis para evitar timeouts e dependência de serviço externo nos testes.
    Bypassa conexões lentas ou inexistentes durante a execução dos testes.
    """
    mock = MagicMock()
    # Configura comportamentos padrão para não quebrar a lógica de negócio
    mock.get.return_value = None
    mock.exists.return_value = 0
    mock.incr.return_value = 1
    mock.ttl.return_value = -1

    # Mock em múltiplos locais para garantir que pegue independentemente da forma de importação
    monkeypatch.setattr("infrastructure.database.get_redis_client", lambda: mock)
    try:
        # Pega o local onde é usado nas dependências do FastAPI
        monkeypatch.setattr(
            "presentation.auth_dependencies.get_redis_client", lambda: mock
        )
    except (ImportError, AttributeError):
        pass

    return mock


@pytest.fixture(autouse=True)
def fast_bcrypt(monkeypatch):
    """
    Reduz o custo do bcrypt durante os testes para acelerar a execução.
    Impacto: 0.18s -> 0.001s por hash.
    """
    import bcrypt

    original_gensalt = bcrypt.gensalt

    def mocked_gensalt(rounds=4):
        return original_gensalt(rounds=4)

    monkeypatch.setattr(bcrypt, "gensalt", mocked_gensalt)


@pytest.fixture
def proposicao_exemplo():
    """Entidade válida reutilizável em qualquer teste."""
    return Proposicao(
        id="12345",
        tipo="PL",
        numero="123",
        ano=2024,
        autor="Autor Exemplo",
        uf_autor="DF",
        status="Em tramitação",
        ementa="Dispõe sobre exemplo de teste",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        orgao_atual="CCJ",
        tags=[],
    )


@pytest.fixture
def lista_proposicoes(proposicao_exemplo):
    """Lista com 3 proposições para testar paginação/filtros."""
    return [
        proposicao_exemplo,
        Proposicao(
            id="12346",
            tipo="PEC",
            numero="45",
            ano=2023,
            autor="Autor 2",
            uf_autor="SP",
            status="Aprovada",
            ementa="Outra proposta",
            data_apresentacao="2023-01-01",
            data_ultima_movimentacao="2023-12-01",
            orgao_atual="Plenário",
            tags=[],
        ),
        Proposicao(
            id="12347",
            tipo="PL",
            numero="124",
            ano=2024,
            autor="Autor 3",
            uf_autor="RJ",
            status="Em tramitação",
            ementa="Mais uma",
            data_apresentacao="2024-02-01",
            data_ultima_movimentacao="2024-02-01",
            orgao_atual="Mesa",
            tags=[],
        ),
    ]

@pytest.fixture
def camara_api_proposicao_json():
    return {
        "dados": {
            "id": 2368289,
            "siglaTipo": "PL",
            "numero": 2981,
            "ano": 2023,
            "ementa": "Altera a Lei nº...",
            "dataApresentacao": "2023-06-05T14:32:00",
            "statusProposicao": {
                "dataHora": "2023-06-20T10:00:00",
                "siglaOrgao": "CCJC",
                "despacho": "Aguardando Parecer",
                "descricaoSituacao": "Pronta para Pauta"
            }
        }
    }

@pytest.fixture
def camara_api_autores_json():
    return {
        "dados": [
            {
                "nome": "João das Couves",
                "siglaUf": "SP"
            }
        ]
    }

@pytest.fixture
def senado_api_materia_json():
    return {
        "DetalheMateria": {
            "Materia": {
                "IdentificacaoMateria": {
                    "DescricaoIdentificacaoMateria": "PL 1234/2023",
                    "IdentificacaoProcesso": "1234567"
                },
                "DadosBasicosMateria": {
                    "EmentaMateria": "Ementa de teste Senado",
                    "DataApresentacao": "2023-01-01",
                    "Autor": "Senador Fulano"
                },
                "SituacaoAtual": {
                    "Autuacoes": {
                        "Autuacao": [
                            {
                                "Situacao": {
                                    "DescricaoSituacao": "Aguardando Relator",
                                    "DataSituacao": "2023-02-01"
                                }
                            }
                        ]
                    }
                }
            }
        }
    }
