import logging

from celery import shared_task
from sqlmodel import Session

from application.services.processar_metricas_service import ProcessarMetricasService
from application.services.recalcular_baselines_service import RecalcularBaselinesService
from infrastructure.database import engine
from infrastructure.repositories.sql_baseline_tramitacao_repository import (
    SQLBaselineTramitacaoRepository,
)
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)

logger = logging.getLogger(__name__)


@shared_task(name="recalcular_baselines_diario")
def task_recalcular_baselines_diario() -> dict:
    """
    Task diária do Celery para limpar e recalcular baselines dinâmicos.
    """
    logger.info("Iniciando task Celery: task_recalcular_baselines_diario")
    try:
        with Session(engine) as session:
            prop_repo = SQLProposicaoRepository(session)
            evento_repo = SQLEventoTramitacaoRepository(session)
            fase_repo = SQLFaseAnaliticaRepository(session)
            baseline_repo = SQLBaselineTramitacaoRepository(session)

            service = RecalcularBaselinesService(
                proposicao_repo=prop_repo,
                evento_repo=evento_repo,
                fase_repo=fase_repo,
                baseline_repo=baseline_repo,
            )
            resumo = service.executar()

            # Invalida o cache do dashboard após recalcular baselines
            try:
                from infrastructure.cache.redis_client import RedisClient
                from infrastructure.database import init_redis
                redis_raw = init_redis()
                cache_provider = RedisClient(redis_raw)
                cache_provider.invalidate("dashboard:")
                logger.info("⚡ Cache do dashboard invalidado após recalcular baselines.")
            except Exception as cache_err:
                logger.error(f"Falha ao invalidar cache após recalcular baselines: {cache_err}")

            logger.info(f"Task finalizada. Resumo: {resumo}")
            return resumo
    except Exception as e:
        logger.error(
            f"Falha na task task_recalcular_baselines_diario: {e}", exc_info=True
        )
        raise e


@shared_task(name="processar_metricas_todas_ativas")
def task_processar_metricas_todas_ativas() -> dict:
    """
    Task do Celery para recalcular as métricas de todas as proposições legislativas.
    """
    logger.info("Iniciando task Celery: task_processar_metricas_todas_ativas")
    try:
        with Session(engine) as session:
            prop_repo = SQLProposicaoRepository(session)
            evento_repo = SQLEventoTramitacaoRepository(session)
            fase_repo = SQLFaseAnaliticaRepository(session)
            baseline_repo = SQLBaselineTramitacaoRepository(session)

            service = ProcessarMetricasService(
                proposicao_repo=prop_repo,
                evento_repo=evento_repo,
                fase_repo=fase_repo,
                baseline_repo=baseline_repo,
            )
            resumo = service.executar()

            # Invalida o cache do dashboard após processar métricas
            try:
                from infrastructure.cache.redis_client import RedisClient
                from infrastructure.database import init_redis
                redis_raw = init_redis()
                cache_provider = RedisClient(redis_raw)
                cache_provider.invalidate("dashboard:")
                logger.info("⚡ Cache do dashboard invalidado após recalcular métricas.")
            except Exception as cache_err:
                logger.error(f"Falha ao invalidar cache após recalcular métricas: {cache_err}")

            logger.info(f"Task finalizada. Resumo: {resumo}")
            return resumo
    except Exception as e:
        logger.error(
            f"Falha na task task_processar_metricas_todas_ativas: {e}", exc_info=True
        )
        raise e
