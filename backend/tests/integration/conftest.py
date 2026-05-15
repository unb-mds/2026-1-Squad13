import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from main import app
from infrastructure.database import get_session
from domain.entities.proposicao import Proposicao


# Banco de dados SQLite em memória para cada teste
@pytest.fixture(name="db_session")
def session_fixture():
    # Usamos StaticPool para manter a conexão aberta em memória durante o teste
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Popular com dados básicos para os testes de busca funcionarem
        session.add(
            Proposicao(
                id="1",
                tipo="PL",
                numero="1",
                ano=2024,
                autor="A",
                uf_autor="DF",
                status="X",
                orgao_atual="O",
                ementa="E",
                data_apresentacao="D",
                data_ultima_movimentacao="D",
                tags=[],
            )
        )
        session.commit()
        yield session


@pytest.fixture
def http_client(db_session):
    """
    Cliente que usa um banco de dados em memória sobrescrevendo a dependência do FastAPI.
    """

    def get_session_override():
        yield db_session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
