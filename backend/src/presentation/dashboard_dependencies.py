from fastapi import Depends
from sqlmodel import Session

from application.services.atualizar_cobertura_service import AtualizarCoberturaService
from application.services.dashboard_service import DashboardService
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.cache.redis_client import RedisClient
from infrastructure.database import get_redis_client, get_session
from infrastructure.repositories.sql_cobertura_snapshot_repository import (
    SQLCoberturaSnapshotRepository,
)
from infrastructure.repositories.sql_dashboard_repository import SQLDashboardRepository
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)


def get_dashboard_repository(
    session: Session = Depends(get_session),
) -> SQLDashboardRepository:
    return SQLDashboardRepository(session)


def get_dashboard_service(
    session: Session = Depends(get_session),
    redis_client: RedisClient = Depends(get_redis_client),
) -> DashboardService:
    dashboard_repo = SQLDashboardRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    proposicao_repo = SQLProposicaoRepository(session)
    fase_repo = SQLFaseAnaliticaRepository(session)

    return DashboardService(
        repository=proposicao_repo,
        evento_repo=evento_repo,
        fase_repo=fase_repo,
        cache_provider=redis_client,
        dashboard_repo=dashboard_repo,
    )


def get_cobertura_repository(
    session: Session = Depends(get_session),
) -> SQLCoberturaSnapshotRepository:
    return SQLCoberturaSnapshotRepository(session)


def get_atualizar_cobertura_service(
    session: Session = Depends(get_session),
    cobertura_repo: SQLCoberturaSnapshotRepository = Depends(get_cobertura_repository),
) -> AtualizarCoberturaService:
    proposicao_repo = SQLProposicaoRepository(session)
    return AtualizarCoberturaService(
        cobertura_repo=cobertura_repo,
        proposicao_repo=proposicao_repo,
        camara_adapter=CamaraAdapter(),
        senado_adapter=SenadoAdapter(),
    )
