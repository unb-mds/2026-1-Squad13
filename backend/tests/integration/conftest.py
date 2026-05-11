import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from main import app
from infrastructure.database import get_session
from domain.entities.proposicao import Proposicao

# Banco de dados SQLite em arquivo para testes de integração da API
sqlite_url = "sqlite:///./test_db.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

@pytest.fixture(name="db_session")
def session_fixture():
    # Garante que as tabelas existem
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Limpa dados de testes anteriores
        session.exec(select(Proposicao)).all() # Apenas para garantir carregamento
        for p in session.exec(select(Proposicao)).all():
            session.delete(p)
        
        # Popular com dados básicos para os testes de busca funcionarem
        session.add(Proposicao(
            id=1, tipo="PL", numero=1, ano=2024, autor="A", uf_autor="DF", 
            status_tramitacao="X", ementa="E", data_apresentacao="D", 
            data_ultima_movimentacao="D", orgao_atual="O", tags=[]
        ))
        session.commit()
        yield session
    
    # Não removemos o arquivo, apenas limpamos para o próximo teste

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
