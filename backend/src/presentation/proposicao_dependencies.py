import redis
from fastapi import Depends
from sqlmodel import Session

from application.services.buscar_proposicoes_service import BuscarProposicoesService
from application.services.detalhe_proposicao_service import DetalheProposicaoService
from application.services.gerar_estimativa_service import GerarEstimativaUseCase
from application.services.listar_movimentacoes_service import (
    ListarMovimentacoesService,
)
from application.services.obter_confiabilidade_service import (
    ObterConfiabilidadeService,
)
from application.services.reconstruir_periodos_service import ReconstruirPeriodosService
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.cache.redis_client import RedisClient
from infrastructure.database import get_redis_client, get_session
from infrastructure.repositories.sql_apensamento_repository import (
    SQLApensamentoRepository,
)
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_orgao_legislativo_repository import (
    SQLOrgaoLegislativoRepository,
)
from infrastructure.repositories.sql_periodo_fase_repository import (
    SQLPeriodoFaseRepository,
)
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)


def get_proposicao_repository(
    session: Session = Depends(get_session),
) -> SQLProposicaoRepository:
    return SQLProposicaoRepository(session)


def get_buscar_proposicoes_service(
    repository: SQLProposicaoRepository = Depends(get_proposicao_repository),
) -> BuscarProposicoesService:
    return BuscarProposicoesService(repository)


def get_detalhe_proposicao_service(
    repository: SQLProposicaoRepository = Depends(get_proposicao_repository),
) -> DetalheProposicaoService:
    return DetalheProposicaoService(repository, CamaraAdapter(), SenadoAdapter())


def get_reconstruir_periodos_service(
    session: Session = Depends(get_session),
) -> ReconstruirPeriodosService:
    periodo_repo = SQLPeriodoFaseRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    fase_repo = SQLFaseAnaliticaRepository(session)
    proposicao_repo = SQLProposicaoRepository(session)

    return ReconstruirPeriodosService(
        periodo_repo=periodo_repo,
        evento_repo=evento_repo,
        fase_repo=fase_repo,
        proposicao_repo=proposicao_repo,
    )


def get_cache_provider(
    redis_raw: redis.Redis = Depends(get_redis_client),
) -> RedisClient:
    return RedisClient(redis_raw)


def get_listar_movimentacoes_service(
    session: Session = Depends(get_session),
    reconstruir_service: ReconstruirPeriodosService = Depends(
        get_reconstruir_periodos_service
    ),
    cache_provider: RedisClient = Depends(get_cache_provider),
) -> ListarMovimentacoesService:
    # Este serviço precisa de múltiplos repositórios e adapters
    evento_repo = SQLEventoTramitacaoRepository(session)
    proposicao_repo = SQLProposicaoRepository(session)
    fase_repo = SQLFaseAnaliticaRepository(session)
    orgao_repo = SQLOrgaoLegislativoRepository(session)
    apensamento_repo = SQLApensamentoRepository(session)

    return ListarMovimentacoesService(
        evento_repo=evento_repo,
        proposicao_repo=proposicao_repo,
        fase_repo=fase_repo,
        orgao_repo=orgao_repo,
        camara_adapter=CamaraAdapter(),
        senado_adapter=SenadoAdapter(),
        apensamento_repo=apensamento_repo,
        reconstruir_service=reconstruir_service,
        cache_provider=cache_provider,
    )


def get_gerar_estimativa_use_case(
    repository: SQLProposicaoRepository = Depends(get_proposicao_repository),
) -> GerarEstimativaUseCase:
    from infrastructure.config import settings

    return GerarEstimativaUseCase(
        repository=repository,
        threshold_minimo_amostra=settings.THRESHOLD_MINIMO_AMOSTRA_ESTIMATIVA,
    )


def get_obter_confiabilidade_service(
    session: Session = Depends(get_session),
) -> ObterConfiabilidadeService:
    proposicao_repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    return ObterConfiabilidadeService(proposicao_repo, evento_repo)
