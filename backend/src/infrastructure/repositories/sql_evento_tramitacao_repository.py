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
from infrastructure.database.models.evento_tramitacao_model import EventoTramitacaoModel


class SQLEventoTramitacaoRepository:
    """Repositório SQL para eventos de tramitação."""

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: EventoTramitacaoModel) -> EventoTramitacao:
        return EventoTramitacao.model_validate(model.model_dump())

    def _to_model(self, entity: EventoTramitacao) -> EventoTramitacaoModel:
        return EventoTramitacaoModel.model_validate(entity.model_dump())

    def salvar(self, evento: EventoTramitacao) -> EventoTramitacao:
        """Persiste um único evento de tramitação."""
        model = self._to_model(evento)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def salvar_lote(self, eventos: List[EventoTramitacao]) -> List[EventoTramitacao]:
        """Persiste uma lista de eventos em batch usando add_all."""
        if eventos:
            models = [self._to_model(e) for e in eventos]
            self.session.add_all(models)
            self.session.commit()
        return eventos

    def existe_algum_evento(self, proposicao_id: str) -> bool:
        """Verifica se existe pelo menos um evento para a proposição."""
        statement = select(func.count()).where(
            EventoTramitacaoModel.proposicao_id == proposicao_id
        )
        count = self.session.exec(statement).one()
        return count > 0

    def buscar_por_proposicao(
        self, proposicao_id: str, somente_relevantes: bool = False
    ) -> List[EventoTramitacao]:
        """
        Retorna eventos de uma proposição ordenados cronologicamente.
        Opcionalmente filtra apenas os marcados como relevantes.
        """
        statement = select(EventoTramitacaoModel).where(
            EventoTramitacaoModel.proposicao_id == proposicao_id
        )

        if somente_relevantes:
            statement = statement.where(EventoTramitacaoModel.relevante == True)

        statement = statement.order_by(
            EventoTramitacaoModel.data_evento.asc(),
            EventoTramitacaoModel.sequencia.asc(),
        )
        models = self.session.exec(statement).all()
        return [self._to_entity(m) for m in models]

    def buscar_por_multiplas_proposicoes(
        self, proposicoes_ids: List[str]
    ) -> Dict[str, List[EventoTramitacao]]:
        """
        Retorna eventos para múltiplas proposições de uma só vez (batch query),
        agrupados por proposicao_id e ordenados cronologicamente.
        """
        if not proposicoes_ids:
            return {}

        statement = (
            select(EventoTramitacaoModel)
            .where(EventoTramitacaoModel.proposicao_id.in_(proposicoes_ids))
            .order_by(
                EventoTramitacaoModel.proposicao_id.asc(),
                EventoTramitacaoModel.data_evento.asc(),
                EventoTramitacaoModel.sequencia.asc(),
            )
        )

        resultados = self.session.exec(statement).all()

        agrupado: Dict[str, List[EventoTramitacao]] = {
            pid: [] for pid in proposicoes_ids
        }
        for m in resultados:
            agrupado[m.proposicao_id].append(self._to_entity(m))

        return agrupado

    def buscar_ultimo_evento(self, proposicao_id: str) -> Optional[EventoTramitacao]:
        """Retorna o evento mais recente de uma proposição."""
        statement = (
            select(EventoTramitacaoModel)
            .where(EventoTramitacaoModel.proposicao_id == proposicao_id)
            .order_by(
                EventoTramitacaoModel.data_evento.desc(),
                EventoTramitacaoModel.sequencia.desc(),
            )
            .limit(1)
        )
        model = self.session.exec(statement).first()
        return self._to_entity(model) if model else None

    def deletar_por_proposicao(self, proposicao_id: str) -> None:
        """Remove todos os eventos de uma proposição (útil para re-sync)."""
        statement = select(EventoTramitacaoModel).where(
            EventoTramitacaoModel.proposicao_id == proposicao_id
        )
        resultados = self.session.exec(statement).all()
        for r in resultados:
            self.session.delete(r)
        self.session.commit()

    def contar_por_tipo(self, proposicao_id: str) -> Dict[str, int]:
        """
        Retorna contagem de eventos agrupados por tipo_evento.
        """
        statement = (
            select(
                EventoTramitacaoModel.tipo_evento,
                func.count().label("total"),
            )
            .where(EventoTramitacaoModel.proposicao_id == proposicao_id)
            .group_by(EventoTramitacaoModel.tipo_evento)
        )
        resultados = self.session.exec(statement).all()
        return {row[0]: row[1] for row in resultados}
