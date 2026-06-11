from typing import Optional

import redis
from sqlmodel import Session, SQLModel, create_engine

from infrastructure.database.models.apensamento_model import (
    ApensamentoModel,  # noqa: F401
)
from infrastructure.database.models.evento_tramitacao_model import (
    EventoTramitacaoModel,  # noqa: F401
)
from infrastructure.database.models.fase_analitica_model import (
    FaseAnaliticaModel,  # noqa: F401
)
from infrastructure.database.models.orgao_legislativo_model import (
    OrgaoLegislativoModel,  # noqa: F401
)

# Importando modelos para garantir que sejam registrados antes de init_db
from infrastructure.database.models.proposicao_model import (
    ProposicaoModel,  # noqa: F401
)
from infrastructure.database.models.user_model import UserModel  # noqa: F401

from ..config import settings

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


# Cliente Redis único (Singleton) para gerenciar o pool de conexões
redis_client: Optional[redis.Redis] = None


def init_redis():
    """Inicializa o cliente Redis único se ainda não estiver configurado."""
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_timeout=2.0,
            socket_connect_timeout=2.0,
        )
    return redis_client


def close_redis():
    """Fecha a conexão com o Redis de forma segura."""
    global redis_client
    if redis_client:
        redis_client.close()
        redis_client = None


def get_redis_client() -> redis.Redis:
    """
    Retorna a instância global do cliente Redis.
    Se não estiver inicializada, inicializa.
    """
    if redis_client is None:
        return init_redis()
    return redis_client
