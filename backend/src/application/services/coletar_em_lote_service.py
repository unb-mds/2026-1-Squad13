import asyncio
import logging

import httpx

from application.ports.apensamento_repository import ApensamentoRepositoryPort
from application.ports.camara_adapter import CamaraAdapterPort
from application.ports.evento_tramitacao_repository import (
    EventoTramitacaoRepositoryPort,
)
from application.ports.fase_analitica_repository import (
    FaseAnaliticaRepositoryPort,
)
from application.ports.log_coleta_repository import LogColetaRepositoryPort
from application.ports.orgao_legislativo_repository import (
    OrgaoLegislativoRepositoryPort,
)
from application.ports.proposicao_repository import ProposicaoRepositoryPort
from application.ports.senado_adapter import SenadoAdapterPort
from application.services.listar_movimentacoes_service import ListarMovimentacoesService
from domain.entities.proposicao import Proposicao

logger = logging.getLogger(__name__)


class ColetarEmLoteService:
    """
    Serviço de aplicação responsável pela orquestração da coleta de proposições em lote
    da Câmara e do Senado, garantindo persistência idempotente e isolamento de falhas.
    """

    def __init__(
        self,
        repository: ProposicaoRepositoryPort,
        evento_repo: EventoTramitacaoRepositoryPort,
        fase_repo: FaseAnaliticaRepositoryPort,
        orgao_repo: OrgaoLegislativoRepositoryPort,
        apensamento_repo: ApensamentoRepositoryPort,
        log_repo: LogColetaRepositoryPort,
        camara_adapter: CamaraAdapterPort,
        senado_adapter: SenadoAdapterPort,
    ):
        self.repository = repository
        self.evento_repo = evento_repo
        self.fase_repo = fase_repo
        self.orgao_repo = orgao_repo
        self.apensamento_repo = apensamento_repo
        self.log_repo = log_repo
        self.camara_adapter = camara_adapter
        self.senado_adapter = senado_adapter

        self.listar_movimentacoes_service = ListarMovimentacoesService(
            evento_repo=self.evento_repo,
            proposicao_repo=self.repository,
            fase_repo=self.fase_repo,
            orgao_repo=self.orgao_repo,
            camara_adapter=self.camara_adapter,
            senado_adapter=self.senado_adapter,
            apensamento_repo=self.apensamento_repo,
        )

    async def executar_coleta_diaria(self) -> dict:
        """
        Orquestra a coleta diária de ambas as fontes (Câmara e Senado).
        Retorna um resumo da execução.
        """
        resumo = {
            "camara": {"status": "pendente", "itens_coletados": 0, "erro": None},
            "senado": {"status": "pendente", "itens_coletados": 0, "erro": None},
        }

        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            # Coleta Câmara (Meta: 300)
            try:
                logger.info(
                    "Iniciando coleta em lote da Câmara dos Deputados (Meta: 300)..."
                )
                props_camara = await self.camara_adapter.coletar_em_lote(
                    {"limite_total": 300}
                )
                if props_camara:
                    await self._processar_proposicoes(props_camara, client)

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
                props_senado = await self.senado_adapter.coletar_em_lote(
                    {"limite_total": 200}
                )
                if props_senado:
                    await self._processar_proposicoes(props_senado, client)

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

    async def _processar_proposicoes(
        self, proposicoes: list[Proposicao], client: httpx.AsyncClient
    ):
        """Salva proposições e coleta seus eventos de tramitação."""
        # 1. Upsert das proposições (rápido)
        self.repository.upsert_em_lote_por_numero_canonico(proposicoes)

        # 2. Coleta de eventos (demorado, fazemos em pequenos batches para não estourar)
        batch_size = 10
        for i in range(0, len(proposicoes), batch_size):
            batch = proposicoes[i : i + batch_size]
            tasks = []
            for prop in batch:
                # O real_id no banco pode ser diferente do id da API se houve normalização,
                # mas aqui usamos o ID que acabamos de salvar.
                tasks.append(
                    self.listar_movimentacoes_service.executar(prop.id, client=client)
                )

            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info(
                f"Processados eventos para {min(i + batch_size, len(proposicoes))}/{len(proposicoes)} proposições."
            )

    def _registrar_log(self, fonte: str, status: str, itens: int, erro: str = None):
        """Registra o log de execução no banco de dados."""
        self.log_repo.salvar_log(
            fonte=fonte,
            status=status,
            itens_coletados=itens,
            mensagem_erro=erro,
        )
