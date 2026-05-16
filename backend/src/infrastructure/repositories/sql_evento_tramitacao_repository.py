"""
Repositório para persistência de EventoTramitacao.

Substitui o antigo SQLTramitacaoRepository, operando sobre a nova
entidade analítica que inclui tipo_evento, fase_analitica_id e flags
de controle.

Ordenação padrão: data_evento ASC, sequencia ASC (cronológica).
"""

from typing import Dict, List, Optional

from sqlalchemy import func
from sqlmodel import Session, select

from domain.entities.evento_tramitacao import EventoTramitacao


class SQLEventoTramitacaoRepository:
    """Repositório SQL para eventos de tramitação."""

    def __init__(self, session: Session):
        self.session = session

    def salvar(self, evento: EventoTramitacao) -> EventoTramitacao:
        """Persiste um único evento de tramitação."""
        self.session.add(evento)
        self.session.commit()
        self.session.refresh(evento)
        return evento

    def salvar_lote(self, eventos: List[EventoTramitacao]) -> List[EventoTramitacao]:
        """Persiste uma lista de eventos em batch usando add_all."""
        if eventos:
            self.session.add_all(eventos)
            self.session.commit()
        return eventos

    def buscar_por_proposicao(
        self, proposicao_id: str
    ) -> List[EventoTramitacao]:
        """
        Retorna todos os eventos de uma proposição ordenados
        cronologicamente (data_evento ASC, sequencia ASC).
        """
        statement = (
            select(EventoTramitacao)
            .where(EventoTramitacao.proposicao_id == proposicao_id)
            .order_by(
                EventoTramitacao.data_evento.asc(),
                EventoTramitacao.sequencia.asc(),
            )
        )
        return list(self.session.exec(statement).all())

    def buscar_por_multiplas_proposicoes(
        self, proposicoes_ids: List[str]
    ) -> Dict[str, List[EventoTramitacao]]:
        """
        Retorna eventos para múltiplas proposições de uma só vez (batch query),
        agrupados por proposicao_id e ordenados cronologicamente.
        Resolve o problema de N+1 no DashboardService.
        """
        if not proposicoes_ids:
            return {}

        statement = (
            select(EventoTramitacao)
            .where(EventoTramitacao.proposicao_id.in_(proposicoes_ids))
            .order_by(
                EventoTramitacao.proposicao_id.asc(),
                EventoTramitacao.data_evento.asc(),
                EventoTramitacao.sequencia.asc(),
            )
        )
        
        resultados = self.session.exec(statement).all()
        
        agrupado: Dict[str, List[EventoTramitacao]] = {pid: [] for pid in proposicoes_ids}
        for e in resultados:
            agrupado[e.proposicao_id].append(e)
            
        return agrupado

    def buscar_ultimo_evento(
        self, proposicao_id: str
    ) -> Optional[EventoTramitacao]:
        """Retorna o evento mais recente de uma proposição."""
        statement = (
            select(EventoTramitacao)
            .where(EventoTramitacao.proposicao_id == proposicao_id)
            .order_by(
                EventoTramitacao.data_evento.desc(),
                EventoTramitacao.sequencia.desc(),
            )
            .limit(1)
        )
        return self.session.exec(statement).first()

    def deletar_por_proposicao(self, proposicao_id: str) -> None:
        """Remove todos os eventos de uma proposição (útil para re-sync)."""
        statement = select(EventoTramitacao).where(
            EventoTramitacao.proposicao_id == proposicao_id
        )
        resultados = self.session.exec(statement).all()
        for r in resultados:
            self.session.delete(r)
        self.session.commit()

    def contar_por_tipo(self, proposicao_id: str) -> Dict[str, int]:
        """
        Retorna contagem de eventos agrupados por tipo_evento.

        Útil para métricas de cobertura do classificador e
        distribuição de tipos por proposição.
        """
        statement = (
            select(
                EventoTramitacao.tipo_evento,
                func.count().label("total"),
            )
            .where(EventoTramitacao.proposicao_id == proposicao_id)
            .group_by(EventoTramitacao.tipo_evento)
        )
        resultados = self.session.exec(statement).all()
        return {row[0]: row[1] for row in resultados}
