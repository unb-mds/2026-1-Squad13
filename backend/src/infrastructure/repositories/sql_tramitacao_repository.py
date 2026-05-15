from typing import List
from sqlmodel import Session, select
from domain.entities.tramitacao import Tramitacao

class SQLTramitacaoRepository:
    """
    Repositório para persistência de tramitações.
    """
    def __init__(self, session: Session):
        self.session = session

    def salvar_lote(self, tramitacoes: List[Tramitacao]) -> List[Tramitacao]:
        """Salva uma lista de tramitações no banco."""
        for t in tramitacoes:
            self.session.add(t)
        self.session.commit()
        return tramitacoes

    def buscar_por_proposicao(self, proposicao_id: str) -> List[Tramitacao]:
        """Busca todas as tramitações de uma proposição ordenadas por data e sequência."""
        statement = (
            select(Tramitacao)
            .where(Tramitacao.proposicao_id == proposicao_id)
            .order_by(Tramitacao.data_hora.desc(), Tramitacao.sequencia.desc())
        )
        return list(self.session.exec(statement).all())

    def deletar_por_proposicao(self, proposicao_id: str):
        """Remove todas as tramitações de uma proposição (útil para atualizar o cache)."""
        statement = select(Tramitacao).where(Tramitacao.proposicao_id == proposicao_id)
        resultados = self.session.exec(statement).all()
        for r in resultados:
            self.session.delete(r)
        self.session.commit()
