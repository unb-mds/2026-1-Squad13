from sqlmodel import SQLModel, create_engine, Session
from .config import settings

# Importando modelos para garantir que sejam registrados antes de init_db
from domain.entities.proposicao import Proposicao  # noqa: F401
from domain.entities.user import User  # noqa: F401

# O motor de conexão (Engine)
# echo=True faz com que o SQLModel imprima os comandos SQL no console (útil para aprender)
engine = create_engine(settings.database_url, echo=True)

def init_db():
    """Cria as tabelas no banco de dados se elas não existirem"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Generator que fornece uma sessão de banco de dados.
    Garante que a conexão seja fechada após o uso.
    """
    with Session(engine) as session:
        yield session
