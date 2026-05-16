"""
Testes de infraestrutura para SQLFaseAnaliticaRepository.

Valida seed idempotente das 8 fases, busca por código e ordenação.
"""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from domain.entities.fase_analitica import FASES_SEED
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)


@pytest.fixture(name="session")
def session_fixture():
    """Cria banco SQLite in-memory com tabela fase_analitica."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_seed_fases_insere_8_registros(session: Session):
    repo = SQLFaseAnaliticaRepository(session)

    repo.seed_fases()
    fases = repo.buscar_todas()

    assert len(fases) == 8


def test_seed_fases_idempotente(session: Session):
    """Rodar seed 2x não deve duplicar registros."""
    repo = SQLFaseAnaliticaRepository(session)

    repo.seed_fases()
    repo.seed_fases()
    fases = repo.buscar_todas()

    assert len(fases) == 8


def test_buscar_por_codigo_existente(session: Session):
    repo = SQLFaseAnaliticaRepository(session)
    repo.seed_fases()

    fase = repo.buscar_por_codigo("PROTOCOLO_INICIAL")

    assert fase is not None
    assert fase.nome == "Protocolo inicial"
    assert fase.ordem_logica == 1


def test_buscar_por_codigo_inexistente(session: Session):
    repo = SQLFaseAnaliticaRepository(session)
    repo.seed_fases()

    fase = repo.buscar_por_codigo("FASE_INEXISTENTE")

    assert fase is None


def test_buscar_todas_ordenadas(session: Session):
    repo = SQLFaseAnaliticaRepository(session)
    repo.seed_fases()

    fases = repo.buscar_todas()

    # Verificar que estão na ordem lógica correta
    assert fases[0].codigo == "PROTOCOLO_INICIAL"
    assert fases[0].ordem_logica == 1
    assert fases[-1].codigo == "ENCERRADA"
    assert fases[-1].ordem_logica == 8

    # Verificar que a lista está monotonicamente crescente
    for i in range(1, len(fases)):
        assert fases[i].ordem_logica > fases[i - 1].ordem_logica


def test_seed_codigos_correspondem_a_fases_seed(session: Session):
    """Garante que os códigos no banco correspondem exatamente ao FASES_SEED."""
    repo = SQLFaseAnaliticaRepository(session)
    repo.seed_fases()

    fases = repo.buscar_todas()
    codigos_banco = {f.codigo for f in fases}
    codigos_seed = {f["codigo"] for f in FASES_SEED}

    assert codigos_banco == codigos_seed
