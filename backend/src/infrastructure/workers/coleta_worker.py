import asyncio
import logging

from celery import shared_task
from sqlmodel import Session

from application.services.coletar_em_lote_service import ColetarEmLoteService
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.database import engine
from infrastructure.repositories.sql_apensamento_repository import (
    SQLApensamentoRepository,
)
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_log_coleta_repository import (
    SQLLogColetaRepository,
)
from infrastructure.repositories.sql_orgao_legislativo_repository import (
    SQLOrgaoLegislativoRepository,
)
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)

logger = logging.getLogger(__name__)


@shared_task(name="coletar_proposicoes_diario")
def task_coletar_proposicoes_diario():
    """
    Task diária do Celery para buscar proposições em lote (Câmara e Senado).
    Delega a orquestração para o Application Service.
    """
    logger.info("Iniciando worker: task_coletar_proposicoes_diario")

    async def _run():
        with Session(engine) as session:
            repository = SQLProposicaoRepository(session)
            evento_repo = SQLEventoTramitacaoRepository(session)
            fase_repo = SQLFaseAnaliticaRepository(session)
            orgao_repo = SQLOrgaoLegislativoRepository(session)
            apensamento_repo = SQLApensamentoRepository(session)
            log_repo = SQLLogColetaRepository(session)
            camara_adapter = CamaraAdapter()
            senado_adapter = SenadoAdapter()

            service = ColetarEmLoteService(
                repository=repository,
                evento_repo=evento_repo,
                fase_repo=fase_repo,
                orgao_repo=orgao_repo,
                apensamento_repo=apensamento_repo,
                log_repo=log_repo,
                camara_adapter=camara_adapter,
                senado_adapter=senado_adapter,
            )
            return await service.executar_coleta_diaria()

    resumo = asyncio.run(_run())

    logger.info(f"Worker finalizado. Resumo: {resumo}")
    return resumo
