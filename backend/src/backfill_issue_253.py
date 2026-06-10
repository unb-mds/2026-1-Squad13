"""
Script de Backfill para Issue 253.
Atualiza o campo numero_emendas de proposições que estão com valor NULL (ou 0 para a Câmara).
"""

import asyncio
import logging
import sys

import httpx
from sqlmodel import select

from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.database import get_session
from infrastructure.database.models.proposicao_model import ProposicaoModel
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("backfill_emendas")


async def backfill():
    logger.info("🚀 Iniciando backfill de emendas (Issue 253)...")

    camara = CamaraAdapter()
    senado = SenadoAdapter()

    async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
        with next(get_session()) as session:
            repo = SQLProposicaoRepository(session)

            # Busca proposições que precisam de atualização:
            # 1. numero_emendas é NULL (novo padrão)
            # 2. numero_emendas é 0 E é da Câmara (provavelmente afetadas pelo bug do endpoint antigo)
            statement = select(ProposicaoModel).where(
                (ProposicaoModel.numero_emendas == None)
                | (
                    (ProposicaoModel.numero_emendas == 0)
                    & (ProposicaoModel.orgao_origem == "Câmara dos Deputados")
                )
            )
            proposicoes_model = session.exec(statement).all()

            if not proposicoes_model:
                logger.info("✅ Nenhuma proposição precisando de backfill de emendas.")
                return

            logger.info(f"📦 Encontradas {len(proposicoes_model)} proposições para atualizar.")

            atualizadas = 0
            falhas = 0

            for model in proposicoes_model:
                try:
                    source = (
                        "camara"
                        if model.orgao_origem == "Câmara dos Deputados"
                        else "senado"
                    )
                    adapter = camara if source == "camara" else senado

                    logger.info(
                        f"   🔎 Atualizando {model.tipo} {model.numero}/{model.ano} ({source})..."
                    )

                    # Re-coleta os dados detalhados para obter o número de emendas
                    p_atualizada = await adapter.buscar_por_id(model.id, client=client)

                    if p_atualizada:
                        model.numero_emendas = p_atualizada.numero_emendas
                        session.add(model)
                        atualizadas += 1
                    
                    # Commita a cada 10 para evitar transações muito longas
                    if atualizadas % 10 == 0:
                        session.commit()

                except Exception as e:
                    logger.error(f"   ❌ Erro em {model.id}: {e}")
                    falhas += 1

            session.commit()
            logger.info(
                f"✨ Backfill finalizado! Atualizadas: {atualizadas}, Falhas: {falhas}"
            )


if __name__ == "__main__":
    try:
        asyncio.run(backfill())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.exception(f"💥 Erro fatal no backfill: {e}")
        sys.exit(1)
