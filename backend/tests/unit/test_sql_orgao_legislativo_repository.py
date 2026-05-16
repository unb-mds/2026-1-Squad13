"""
Testes de infraestrutura para SQLOrgaoLegislativoRepository.

Valida seed idempotente dos órgãos mínimos, upsert por (sigla, casa)
e busca por sigla.
"""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from domain.entities.orgao_legislativo import (
    CasaLegislativa,
)
from infrastructure.repositories.sql_orgao_legislativo_repository import (
    SQLOrgaoLegislativoRepository,
)


@pytest.fixture(name="session")
def session_fixture():
    """Cria banco SQLite in-memory com tabela orgaolegislativo."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_seed_orgaos_insere_3_registros(session: Session):
    repo = SQLOrgaoLegislativoRepository(session)

    repo.seed_orgaos()

    orgaos = repo.buscar_por_sigla("PLEN")
    assert len(orgaos) >= 1

    # Verificar que existem exatamente 3 órgãos no total (PLEN, MESA, SECCJ)
    total = len(repo.buscar_por_sigla("PLEN")) + \
            len(repo.buscar_por_sigla("MESA")) + \
            len(repo.buscar_por_sigla("SECCJ"))
    assert total == 3


def test_seed_orgaos_idempotente(session: Session):
    """Rodar seed 2x não deve duplicar registros."""
    repo = SQLOrgaoLegislativoRepository(session)

    repo.seed_orgaos()
    repo.seed_orgaos()

    total = len(repo.buscar_por_sigla("PLEN")) + \
            len(repo.buscar_por_sigla("MESA")) + \
            len(repo.buscar_por_sigla("SECCJ"))
    assert total == 3


def test_buscar_ou_criar_cria_novo(session: Session):
    repo = SQLOrgaoLegislativoRepository(session)

    orgao = repo.buscar_ou_criar(
        sigla="CCJC",
        casa=CasaLegislativa.CAMARA,
        nome="Comissão de Constituição e Justiça",
    )

    assert orgao.id is not None
    assert orgao.sigla == "CCJC"
    assert orgao.casa == CasaLegislativa.CAMARA


def test_buscar_ou_criar_retorna_existente(session: Session):
    """Não deve duplicar órgão com mesma sigla+casa."""
    repo = SQLOrgaoLegislativoRepository(session)

    orgao1 = repo.buscar_ou_criar(
        sigla="CCJC",
        casa=CasaLegislativa.CAMARA,
        nome="Comissão de Constituição e Justiça",
    )
    orgao2 = repo.buscar_ou_criar(
        sigla="CCJC",
        casa=CasaLegislativa.CAMARA,
        nome="Nome diferente — deve ignorar",
    )

    assert orgao1.id == orgao2.id


def test_buscar_ou_criar_diferencia_por_casa(session: Session):
    """Mesma sigla em casas diferentes deve criar registros distintos."""
    repo = SQLOrgaoLegislativoRepository(session)

    orgao_camara = repo.buscar_ou_criar(
        sigla="CCJ",
        casa=CasaLegislativa.CAMARA,
        nome="CCJ Câmara",
    )
    orgao_senado = repo.buscar_ou_criar(
        sigla="CCJ",
        casa=CasaLegislativa.SENADO,
        nome="CCJ Senado",
    )

    assert orgao_camara.id != orgao_senado.id


def test_buscar_por_sigla(session: Session):
    repo = SQLOrgaoLegislativoRepository(session)
    repo.buscar_ou_criar("CCJ", CasaLegislativa.CAMARA, "CCJ Câmara")
    repo.buscar_ou_criar("CCJ", CasaLegislativa.SENADO, "CCJ Senado")

    resultados = repo.buscar_por_sigla("CCJ")

    assert len(resultados) == 2


def test_buscar_por_sigla_sem_resultados(session: Session):
    repo = SQLOrgaoLegislativoRepository(session)

    resultados = repo.buscar_por_sigla("INEXISTENTE")

    assert resultados == []
