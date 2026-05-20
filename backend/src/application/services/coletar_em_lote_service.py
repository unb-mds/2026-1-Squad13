import logging
from typing import Optional
from sqlmodel import Session
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)
from infrastructure.database.models.log_coleta_model import LogColetaModel

logger = logging.getLogger(__name__)


class ColetarEmLoteService:
    """
    Serviço de aplicação responsável pela orquestração da coleta de proposições em lote
    da Câmara e do Senado, garantindo persistência idempotente e isolamento de falhas.
    """

    def __init__(
        self,
        session: Session,
        camara_adapter: Optional[CamaraAdapter] = None,
        senado_adapter: Optional[SenadoAdapter] = None,
    ):
        self.session = session
        self.repository = SQLProposicaoRepository(session)
        self.camara_adapter = camara_adapter or CamaraAdapter()
        self.senado_adapter = senado_adapter or SenadoAdapter()

    async def executar_coleta_diaria(self) -> dict:
        """
        Orquestra a coleta diária de ambas as fontes (Câmara e Senado).
        Retorna um resumo da execução.
        """
        resumo = {
            "camara": {"status": "pendente", "itens_coletados": 0, "erro": None},
            "senado": {"status": "pendente", "itens_coletados": 0, "erro": None},
        }

        # Coleta Câmara (Meta: 300)
        try:
            logger.info("Iniciando coleta em lote da Câmara dos Deputados (Meta: 300)...")
            props_camara = await self.camara_adapter.coletar_em_lote({"limite_total": 300})
            if props_camara:
                self.repository.upsert_em_lote_por_numero_canonico(props_camara)

            resumo["camara"]["status"] = "sucesso"
            resumo["camara"]["itens_coletados"] = len(props_camara)
            logger.info(f"Câmara finalizada com {len(props_camara)} itens.")
            self._registrar_log("camara", "sucesso", len(props_camara))
        except Exception as e:
            logger.exception("Falha total na coleta da Câmara.")
            resumo["camara"]["status"] = "falha"
            resumo["camara"]["erro"] = str(e)
            self._registrar_log("camara", "falha", 0, str(e))

        # Coleta Senado (Meta: 200)
        try:
            logger.info("Iniciando coleta em lote do Senado Federal (Meta: 200)...")
            props_senado = await self.senado_adapter.coletar_em_lote({"limite_total": 200})
            if props_senado:
                self.repository.upsert_em_lote_por_numero_canonico(props_senado)

            resumo["senado"]["status"] = "sucesso"
            resumo["senado"]["itens_coletados"] = len(props_senado)
            logger.info(f"Senado finalizado com {len(props_senado)} itens.")
            self._registrar_log("senado", "sucesso", len(props_senado))
        except Exception as e:
            logger.exception("Falha total na coleta do Senado.")
            resumo["senado"]["status"] = "falha"
            resumo["senado"]["erro"] = str(e)
            self._registrar_log("senado", "falha", 0, str(e))

        return resumo

    def _registrar_log(self, fonte: str, status: str, itens: int, erro: str = None):
        """Registra o log de execução no banco de dados."""
        log = LogColetaModel(
            fonte=fonte, status=status, itens_coletados=itens, mensagem_erro=erro
        )
        self.session.add(log)
        self.session.commit()
