from typing import List
from domain.entities.tramitacao import Tramitacao
from infrastructure.repositories.sql_tramitacao_repository import (
    SQLTramitacaoRepository,
)
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter


class ListarTramitacoesService:
    """
    Serviço para listar as tramitações de uma proposição.
    Gerencia o cache no banco de dados.
    """

    def __init__(
        self,
        tramitacao_repository: SQLTramitacaoRepository,
        proposicao_repository: SQLProposicaoRepository,
        camara_adapter: CamaraAdapter,
        senado_adapter: SenadoAdapter,
    ):
        self.tramitacao_repository = tramitacao_repository
        self.proposicao_repository = proposicao_repository
        self.camara_adapter = camara_adapter
        self.senado_adapter = senado_adapter

    def executar(self, proposicao_id: str) -> List[Tramitacao]:
        # 0. Se for um Slug (PL-1-2024), tenta encontrar a proposição no banco para obter o ID real
        real_id = proposicao_id
        if "-" in proposicao_id:
            partes = proposicao_id.split("-")
            if len(partes) == 3:
                tipo, numero, ano_str = partes
                try:
                    ano = int(ano_str)
                    p = self.proposicao_repository.buscar_por_codigo(tipo, numero, ano)
                    if p:
                        real_id = str(p.id)
                except ValueError:
                    pass

        # 1. Tenta buscar no banco (cache) usando o ID real
        tramitacoes = self.tramitacao_repository.buscar_por_proposicao(real_id)
        if tramitacoes:
            return tramitacoes

        # 2. Se não encontrou, precisa saber se é da Câmara ou Senado
        proposicao = self.proposicao_repository.buscar_por_id(real_id)

        # Se não temos a proposição no banco, não sabemos qual adapter usar
        if not proposicao:
            # Fallback: tentar descobrir pela origem se o ID for numérico
            if not real_id.isdigit():
                return []

            # Tenta na Câmara primeiro
            tramitacoes = self.camara_adapter.buscar_tramitacoes(int(real_id))
            if not tramitacoes:
                # Tenta no Senado
                tramitacoes = self.senado_adapter.buscar_tramitacoes(int(real_id))
        else:
            if "Câmara" in (proposicao.orgao_origem or ""):
                tramitacoes = self.camara_adapter.buscar_tramitacoes(int(real_id))
            else:
                tramitacoes = self.senado_adapter.buscar_tramitacoes(int(real_id))

        # 3. Salva no cache se encontrou algo
        if tramitacoes:
            self.tramitacao_repository.salvar_lote(tramitacoes)

        return tramitacoes
