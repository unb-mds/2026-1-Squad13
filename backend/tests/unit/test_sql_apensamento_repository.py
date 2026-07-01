import pytest
from sqlmodel import Session, SQLModel, create_engine

from domain.entities.apensamento import Apensamento
from infrastructure.repositories.sql_apensamento_repository import (
    SQLApensamentoRepository,
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

    engine.dispose()


def test_salvar_e_buscar_apensamento(session):
    repo = SQLApensamentoRepository(session)
    ap = Apensamento(
        materia_principal_id="1",
        materia_apensada_id="2",
        data_apensacao="2024-01-01",
        casa="CAMARA",
    )

    salvo = repo.salvar(ap)
    assert salvo.materia_principal_id == "1"

    encontrado = repo.buscar_por_materia_apensada("2")
    assert encontrado is not None
    assert encontrado.materia_principal_id == "1"

    principais = repo.buscar_por_materia_principal("1")
    assert len(principais) == 1
    assert principais[0].materia_apensada_id == "2"


def test_buscar_por_materia_apensada_nao_encontrada(session):
    repo = SQLApensamentoRepository(session)
    assert repo.buscar_por_materia_apensada("non_existent") is None
