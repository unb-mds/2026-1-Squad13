import logging
import asyncio
from celery import shared_task
from sqlmodel import Session
from infrastructure.database import engine
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.repositories.sql_proposicao_repository import SQLProposicaoRepository

logger = logging.getLogger(__name__)

async def _coletar_e_salvar() -> dict:
    camara_adapter = CamaraAdapter()
    senado_adapter = SenadoAdapter()
    
    resumo = {
        "camara": {"status": "pendente", "itens_coletados": 0, "erro": None},
        "senado": {"status": "pendente", "itens_coletados": 0, "erro": None}
    }
    
    with Session(engine) as session:
        repo = SQLProposicaoRepository(session)
        
        # Isolamento de Falha: Câmara
        try:
            logger.info("Iniciando coleta em lote da Câmara dos Deputados...")
            props_camara = await camara_adapter.coletar_em_lote()
            if props_camara:
                repo.upsert_em_lote_por_numero_canonico(props_camara)
            resumo["camara"]["status"] = "sucesso"
            resumo["camara"]["itens_coletados"] = len(props_camara)
            logger.info(f"Câmara finalizada com {len(props_camara)} itens.")
        except Exception as e:
            # Captura exceções para impedir que a falha da Câmara aborte o worker inteiro
            logger.exception("Falha total na coleta da Câmara.")
            resumo["camara"]["status"] = "falha"
            resumo["camara"]["erro"] = str(e)

        # Isolamento de Falha: Senado
        try:
            logger.info("Iniciando coleta em lote do Senado Federal...")
            props_senado = await senado_adapter.coletar_em_lote()
            if props_senado:
                repo.upsert_em_lote_por_numero_canonico(props_senado)
            resumo["senado"]["status"] = "sucesso"
            resumo["senado"]["itens_coletados"] = len(props_senado)
            logger.info(f"Senado finalizado com {len(props_senado)} itens.")
        except Exception as e:
            # Captura exceções para impedir que a falha do Senado afete o resultado do worker
            logger.exception("Falha total na coleta do Senado.")
            resumo["senado"]["status"] = "falha"
            resumo["senado"]["erro"] = str(e)
            
    return resumo

@shared_task(name="coletar_proposicoes_diario")
def task_coletar_proposicoes_diario():
    """
    Task diária do Celery para buscar proposições em lote (Câmara e Senado).
    Retorna um resumo da execução para ser visível no log/Flower.
    """
    logger.info("Iniciando worker: task_coletar_proposicoes_diario")
    
    # Como as bibliotecas do httpx estão rodando código assíncrono,
    # precisamos iniciar o event loop do asyncio dentro do worker síncrono do Celery.
    resumo = asyncio.run(_coletar_e_salvar())
    
    logger.info(f"Worker finalizado. Resumo: {resumo}")
    return resumo
