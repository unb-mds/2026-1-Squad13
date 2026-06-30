from application.ports.camara_adapter import CamaraAdapterPort
from application.ports.proposicao_repository import ProposicaoRepositoryPort
from application.ports.senado_adapter import SenadoAdapterPort
from application.services.atualizar_transit_steps_service import (
    AtualizarTransitStepsService,
)
from domain.entities.proposicao import Proposicao


class DetalheProposicaoService:
    """
    Serviço que busca os detalhes de uma proposição.
    Prioriza o banco de dados local e recorre às APIs externas se necessário.
    """

    def __init__(
        self,
        repository: ProposicaoRepositoryPort,
        camara_adapter: CamaraAdapterPort,
        senado_adapter: SenadoAdapterPort,
        atualizar_transit_steps_service: AtualizarTransitStepsService | None = None,
    ):
        self.repository = repository
        self.camara_adapter = camara_adapter
        self.senado_adapter = senado_adapter
        self.atualizar_transit_steps_service = atualizar_transit_steps_service

    async def executar(self, id_proposicao: str) -> Proposicao:
        proposicao = None

        # 1. Tenta identificar se é um ID numérico ou um Código Canônico (Slug)
        # Formato esperado do Slug: PL-123-2023
        if "-" in id_proposicao:
            partes = id_proposicao.split("-")
            if len(partes) == 3:
                tipo, numero, ano_str = partes
                try:
                    ano = int(ano_str)
                    proposicao = self.repository.buscar_por_codigo(tipo, numero, ano)
                except ValueError:
                    pass

        # 2. Tenta buscar no banco local por ID (ID da Câmara/Senado que usamos como PK)
        if not proposicao:
            proposicao = self.repository.buscar_por_id(id_proposicao)

        # 3. Se não encontrou no banco, tenta nas APIs externas (apenas se o ID for numérico)
        if not proposicao:
            try:
                id_int = int(id_proposicao)
            except ValueError:
                raise ValueError(
                    f"Proposição não encontrada: {id_proposicao}"
                ) from None

            # Tenta na Câmara
            proposicao = await self.camara_adapter.buscar_por_id(id_int)
            if proposicao:
                proposicao.atualizar_metricas()
                proposicao.normalizar_campo_status()
                proposicao = self.repository.salvar(proposicao)
            else:
                # Tenta no Senado
                proposicao = await self.senado_adapter.buscar_por_id(id_int)
                if proposicao:
                    proposicao.atualizar_metricas()
                    proposicao.normalizar_campo_status()
                    proposicao = self.repository.salvar(proposicao)

        if not proposicao:
            raise ValueError(
                f"Proposição com ID {id_proposicao} não encontrada em nenhuma fonte."
            )

        # 4. Busca os transit steps do banco (ou calcula se não existirem)
        steps = self.repository.buscar_transit_steps(proposicao.id)
        if not steps and self.atualizar_transit_steps_service:
            try:
                self.atualizar_transit_steps_service.executar(proposicao.id)
                steps = self.repository.buscar_transit_steps(proposicao.id)
            except Exception as e:
                import logging

                logging.error(f"Erro ao computar transit steps: {e}")

        proposicao.transit_steps = steps or []
        return proposicao
