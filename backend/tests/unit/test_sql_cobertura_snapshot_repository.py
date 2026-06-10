from datetime import UTC, datetime

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from domain.entities.cobertura_snapshot import CoberturaSnapshot
from infrastructure.repositories.sql_cobertura_snapshot_repository import (
    SQLCoberturaSnapshotRepository,
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_salvar_e_buscar_snapshot(session: Session):
    repo = SQLCoberturaSnapshotRepository(session)
    dt = datetime.now(UTC)
    snap = CoberturaSnapshot(
        ano=2026, tipo_proposicao="PL", total_api_oficial=150, data_atualizacao=dt
    )

    saved = repo.salvar(snap)
    assert saved.id is not None
    assert saved.total_api_oficial == 150

    fetched = repo.buscar_por_ano_e_tipo(2026, "PL")
    assert fetched is not None
    assert fetched.id == saved.id
    assert fetched.total_api_oficial == 150


def test_salvar_upsert_snapshot(session: Session):
    repo = SQLCoberturaSnapshotRepository(session)
    dt1 = datetime.now(UTC)
    snap1 = CoberturaSnapshot(
        ano=2026, tipo_proposicao="PL", total_api_oficial=150, data_atualizacao=dt1
    )
    saved1 = repo.salvar(snap1)

    dt2 = datetime.now(UTC)
    snap2 = CoberturaSnapshot(
        ano=2026, tipo_proposicao="PL", total_api_oficial=200, data_atualizacao=dt2
    )
    saved2 = repo.salvar(snap2)

    # Devem ter o mesmo ID
    assert saved1.id == saved2.id

    fetched = repo.buscar_por_ano_e_tipo(2026, "PL")
    assert fetched.total_api_oficial == 200


def test_buscar_todos(session: Session):
    repo = SQLCoberturaSnapshotRepository(session)
    dt1 = datetime.now(UTC)
    dt2 = datetime.now(UTC)

    repo.salvar(
        CoberturaSnapshot(
            ano=2025, tipo_proposicao="PL", total_api_oficial=100, data_atualizacao=dt1
        )
    )
    repo.salvar(
        CoberturaSnapshot(
            ano=2026, tipo_proposicao="PEC", total_api_oficial=50, data_atualizacao=dt2
        )
    )

    all_snaps = repo.buscar_todos()
    assert len(all_snaps) == 2
    # Ordenado por data_atualizacao DESC, então o mais recente vem primeiro
    assert all_snaps[0].ano == 2026
    assert all_snaps[1].ano == 2025
