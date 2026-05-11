from typing import List, Optional
from sqlmodel import Session, select
from domain.entities.proposicao import Proposicao

class SQLProposicaoRepository:
    """
    Implementação do repositório utilizando SQLModel e PostgreSQL.
    """
    def __init__(self, session: Session):
        self.session = session

    def salvar(self, proposicao: Proposicao) -> Proposicao:
        """Salva ou atualiza uma proposição no banco."""
        self.session.add(proposicao)
        self.session.commit()
        self.session.refresh(proposicao)
        return proposicao

    def buscar_por_id(self, id: int) -> Optional[Proposicao]:
        return self.session.get(Proposicao, id)

    def filtrar(
        self,
        tipo: Optional[str] = None,
        numero: Optional[int] = None,
        ano: Optional[int] = None,
        autor: Optional[str] = None,
        uf_autor: Optional[str] = None,
        status_tramitacao: Optional[str] = None
    ) -> List[Proposicao]:
        statement = select(Proposicao)
        
        if tipo:
            statement = statement.where(Proposicao.tipo == tipo)
        if numero:
            statement = statement.where(Proposicao.numero == numero)
        if ano:
            statement = statement.where(Proposicao.ano == ano)
        if autor:
            statement = statement.where(Proposicao.autor.contains(autor))
        if uf_autor:
            statement = statement.where(Proposicao.uf_autor == uf_autor)
        if status_tramitacao:
            statement = statement.where(Proposicao.status_tramitacao == status_tramitacao)
        
        results = self.session.exec(statement)
        return list(results.all())
