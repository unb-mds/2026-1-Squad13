from typing import Optional
from domain.entities.proposicao import Proposicao
from infrastructure.repositories.proposicao_repository import ProposicaoRepository
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter

class DetalheProposicaoService:
    """
    Serviço que busca os detalhes de uma proposição.
    Prioriza o banco de dados local e recorre às APIs externas se necessário.
    """
    def __init__(
        self,
        repository: ProposicaoRepository,
        camara_adapter: CamaraAdapter,
        senado_adapter: SenadoAdapter
    ):
        self.repository = repository
        self.camara_adapter = camara_adapter
        self.senado_adapter = senado_adapter

    def executar(self, id_proposicao: str) -> Proposicao:
        # 1. Tenta buscar no banco local
        proposicao = self.repository.buscar_por_id(id_proposicao)
        if proposicao:
            return proposicao

        # 2. Se não encontrou no banco, tenta nas APIs externas
        # Tenta converter o ID para int para os adapters
        try:
            id_int = int(id_proposicao)
        except ValueError:
            raise ValueError(f"ID inválido: {id_proposicao}")

        # Tenta na Câmara
        proposicao = self.camara_adapter.buscar_por_id(id_int)
        if proposicao:
            proposicao.atualizar_metricas()
            # Salva no banco para cache
            return self.repository.salvar(proposicao)

        # Tenta no Senado
        proposicao = self.senado_adapter.buscar_por_id(id_int)
        if proposicao:
            proposicao.atualizar_metricas()
            # Salva no banco para cache
            return self.repository.salvar(proposicao)

        raise ValueError(f"Proposição com ID {id_proposicao} não encontrada em nenhuma fonte.")
