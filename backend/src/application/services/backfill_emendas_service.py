import logging

import httpx
from sqlmodel import Session, select

from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.database.models.proposicao_model import ProposicaoModel
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)

logger = logging.getLogger(__name__)


class BackfillEmendasService:
    """
    Serviço de aplicação para realizar o backfill do número de emendas.
    """

    def __init__(
        self,
        session: Session,
        camara_adapter: CamaraAdapter,
        senado_adapter: SenadoAdapter,
    ):
        self.session = session
        self.repo = SQLProposicaoRepository(session)
        self.camara = camara_adapter
        self.senado = senado_adapter

    async def executar(self):
        """
        Executa o backfill de emendas para proposições com dados ausentes.
        """
        logger.info("🚀 Iniciando processamento de backfill de emendas...")

        # Busca proposições que precisam de atualização
        statement = select(ProposicaoModel).where(
            (ProposicaoModel.numero_emendas is None)
            | (
                (ProposicaoModel.numero_emendas == 0)
                & (ProposicaoModel.orgao_origem == "Câmara dos Deputados")
            )
        )
        proposicoes_model = self.session.exec(statement).all()

        if not proposicoes_model:
            logger.info("✅ Nenhuma proposição precisando de backfill.")
            return {"atualizadas": 0, "falhas": 0}

        logger.info(
            f"📦 Encontradas {len(proposicoes_model)} proposições para atualizar."
        )

        atualizadas = 0
        falhas = 0

        async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
            for model in proposicoes_model:
                try:
                    source = (
                        "camara"
                        if model.orgao_origem == "Câmara dos Deputados"
                        else "senado"
                    )
                    adapter = self.camara if source == "camara" else self.senado

                    logger.info(f"   🔎 Atualizando {model.id} ({source})...")
                    p_atualizada = await adapter.buscar_por_id(model.id, client=client)

                    if p_atualizada:
                        model.numero_emendas = p_atualizada.numero_emendas
                        self.session.add(model)
                        atualizadas += 1

                    if atualizadas % 10 == 0:
                        self.session.commit()

                except Exception as e:
                    logger.error(f"   ❌ Erro em {model.id}: {e}")
                    falhas += 1

            self.session.commit()

        logger.info(
            f"✨ Backfill finalizado! Atualizadas: {atualizadas}, Falhas: {falhas}"
        )
        return {"atualizadas": atualizadas, "falhas": falhas}
