from typing import List
from domain.entities.tramitacao import Tramitacao
from infrastructure.repositories.sql_tramitacao_repository import SQLTramitacaoRepository
from infrastructure.repositories.sql_proposicao_repository import SQLProposicaoRepository
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
        senado_adapter: SenadoAdapter
    ):
        self.tramitacao_repository = tramitacao_repository
        self.proposicao_repository = proposicao_repository
        self.camara_adapter = camara_adapter
        self.senado_adapter = senado_adapter

    def executar(self, proposicao_id: str) -> List[Tramitacao]:
        # 1. Tenta buscar no banco (cache)
        tramitacoes = self.tramitacao_repository.buscar_por_proposicao(proposicao_id)
        if tramitacoes:
            return tramitacoes

        # 2. Se não encontrou, precisa saber se é da Câmara ou Senado
        proposicao = self.proposicao_repository.buscar_por_id(proposicao_id)
        
        # Se não temos a proposição no banco, não sabemos qual adapter usar 
        # (mas teoricamente ela deveria estar lá se o usuário está vendo o detalhe)
        if not proposicao:
            # Fallback: tentar descobrir pela origem se o ID for numérico
            if not proposicao_id.isdigit():
                # No nosso sistema, IDs da Câmara/Senado podem ser puramente numéricos 
                # ou ter prefixos se for customizado. Vamos assumir numérico por enquanto
                # baseado nos adapters existentes.
                return []
            
            # Tenta na Câmara primeiro
            tramitacoes = self.camara_adapter.buscar_tramitacoes(int(proposicao_id))
            if not tramitacoes:
                # Tenta no Senado
                tramitacoes = self.senado_adapter.buscar_tramitacoes(int(proposicao_id))
        else:
            if "Câmara" in proposicao.orgao_origem:
                tramitacoes = self.camara_adapter.buscar_tramitacoes(int(proposicao_id))
            else:
                tramitacoes = self.senado_adapter.buscar_tramitacoes(int(proposicao_id))

        # 3. Salva no cache se encontrou algo
        if tramitacoes:
            self.tramitacao_repository.salvar_lote(tramitacoes)

        return tramitacoes
