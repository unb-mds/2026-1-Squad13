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
from infrastructure.database.models.log_coleta_model import LogColetaModel  # noqa: F401
from infrastructure.database.models.orgao_legislativo_model import (
    OrgaoLegislativoModel,  # noqa: F401
)

from infrastructure.database.models.baseline_tramitacao_model import (
    BaselineTramitacaoModel,  # noqa: F401
)
from infrastructure.database.models.proposicao_model import (
    ProposicaoModel,  # noqa: F401
)
from infrastructure.database.models.user_model import UserModel  # noqa: F401

from ..config import settings

# O motor de conexão (Engine)
# echo=False por padrão para evitar poluição de logs; use logging.getLogger('sqlalchemy.engine') para debug
engine = create_engine(settings.database_url, echo=False)


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
redis_client: redis.Redis | None = None


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
