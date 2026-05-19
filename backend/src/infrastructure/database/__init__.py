import redis
from sqlmodel import SQLModel, create_engine, Session
from ..config import settings

# Importando modelos para garantir que sejam registrados antes de init_db
from infrastructure.database.models.proposicao_model import ProposicaoModel  # noqa: F401
from infrastructure.database.models.user_model import UserModel  # noqa: F401
from infrastructure.database.models.fase_analitica_model import FaseAnaliticaModel  # noqa: F401
from infrastructure.database.models.orgao_legislativo_model import OrgaoLegislativoModel  # noqa: F401
from infrastructure.database.models.evento_tramitacao_model import EventoTramitacaoModel  # noqa: F401
from infrastructure.database.models.apensamento_model import ApensamentoModel  # noqa: F401

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


def get_redis_connection():
    """
    Retorna uma instância do cliente Redis configurada.
    Utiliza decode_responses=True por padrão para facilitar o uso de strings.
    """
    return redis.Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_timeout=2.0,  # Previne travamentos se o Redis estiver lento
    )
