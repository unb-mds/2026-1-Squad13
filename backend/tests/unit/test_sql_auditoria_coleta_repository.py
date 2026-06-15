import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from infrastructure.repositories.sql_auditoria_coleta_repository import (
    SQLAuditoriaColetaRepository,
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


def test_registrar_inicio_e_fim(session: Session):
    repo = SQLAuditoriaColetaRepository(session)
    job_id = "test-job-123"
    nome_job = "coleta_diaria"

    # 1. Registra o início do job
    repo.registrar_inicio(job_id, nome_job)

    # Valida no banco
    ultima = repo.obter_ultima_execucao(nome_job)
    assert ultima is not None
    assert ultima.job_id == job_id
    assert ultima.status == "executando"
    assert ultima.data_fim is None

    # 2. Registra o fim do job com sucesso
    repo.registrar_fim(job_id, status="sucesso", itens_processados=10)

    # Valida no banco
    ultima = repo.obter_ultima_execucao(nome_job)
    assert ultima is not None
    assert ultima.status == "sucesso"
    assert ultima.itens_processados == 10
    assert ultima.data_fim is not None
    assert ultima.mensagem_erro is None


def test_registrar_fim_com_erro(session: Session):
    repo = SQLAuditoriaColetaRepository(session)
    job_id = "test-job-failed"
    nome_job = "coleta_diaria"

    repo.registrar_inicio(job_id, nome_job)
    repo.registrar_fim(
        job_id,
        status="falha",
        itens_processados=0,
        mensagem_erro="Falha de rede",
    )

    ultima = repo.obter_ultima_execucao(nome_job)
    assert ultima is not None
    assert ultima.status == "falha"
    assert ultima.itens_processados == 0
    assert ultima.mensagem_erro == "Falha de rede"
