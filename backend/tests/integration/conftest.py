import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from infrastructure.database import get_session
from infrastructure.database.models.proposicao_model import ProposicaoModel
from main import app


# Engine único para cada worker (processo) do xdist
# Como o xdist usa processos separados, o escopo session aqui
# cria um engine por processo, o que é ideal para SQLite em memória.
@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="db_session")
def session_fixture(engine):
    """
    Fixture que fornece uma sessão de banco de dados com rollback automático.
    Isso evita a recriação de tabelas a cada teste.
    """
    connection = engine.connect()
    # Inicia uma transação externa
    transaction = connection.begin()

    # Cria a sessão vinculada à conexão
    # join_transaction_mode="create_savepoint" permite que o código da aplicação
    # use commit() internamente (via SAVEPOINT) sem afetar a transação externa.
    with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
        # 1. Verificar se a proposição ID '1' já existe para evitar IntegrityError
        # (Em tese, o rollback deveria limpar, mas se algo falhou no rollback anterior
        # ou se a sessão de transação for compartilhada de forma imprevista, isso protege)
        existing = session.get(ProposicaoModel, "1")
        if not existing:
            session.add(
                ProposicaoModel(
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

    # Rollback de TUDO o que aconteceu no teste
    transaction.rollback()
    connection.close()


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
