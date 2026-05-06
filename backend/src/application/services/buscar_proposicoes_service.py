from typing import List, Optional
from domain.entities.proposicao import Proposicao
from infrastructure.repositories.proposicao_repository import ProposicaoRepository

class BuscarProposicoesService:
    """
    Serviço de Aplicação que orquestra a busca de proposições.
    Contém a regra de negócio de que pelo menos um filtro é obrigatório.
    """
    def __init__(self, repository: ProposicaoRepository):
        self.repository = repository

    def executar(
        self,
        tipo: Optional[str] = None,
        numero: Optional[int] = None,
        ano: Optional[int] = None,
        autor: Optional[str] = None,
        uf_autor: Optional[str] = None,
        status_tramitacao: Optional[str] = None
    ) -> List[Proposicao]:
        
        filtros = [tipo, numero, ano, autor, uf_autor, status_tramitacao]
        
        if not any(valor is not None and str(valor).strip() != "" for valor in filtros):
            raise ValueError("Preencha pelo menos um filtro para realizar a busca.")

        return self.repository.filtrar(
            tipo=tipo,
            numero=numero,
            ano=ano,
            autor=autor,
            uf_autor=uf_autor,
            status_tramitacao=status_tramitacao
        )
