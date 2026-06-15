from sqlmodel import Session, select

from domain.entities.baseline_tramitacao import BaselineTramitacao
from infrastructure.database.models.baseline_tramitacao_model import (
    BaselineTramitacaoModel,
)


class SQLBaselineTramitacaoRepository:
    """
    Implementação do repositório de baselines de tramitação utilizando SQLModel e PostgreSQL.
    Opera sobre BaselineTramitacaoModel (infra) e retorna BaselineTramitacao (domínio).
    """

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: BaselineTramitacaoModel) -> BaselineTramitacao:
        return BaselineTramitacao.model_validate(model.model_dump())

    def _to_model(self, entity: BaselineTramitacao) -> BaselineTramitacaoModel:
        return BaselineTramitacaoModel.model_validate(entity.model_dump())

    def salvar(self, baseline: BaselineTramitacao) -> BaselineTramitacao:
        """Salva ou atualiza um baseline no banco de dados."""
        model = self._to_model(baseline)

        # Procura por registro existente com a mesma chave única para evitar conflitos de restrição
        statement = select(BaselineTramitacaoModel).where(
            BaselineTramitacaoModel.escopo == model.escopo,
            BaselineTramitacaoModel.tipo == model.tipo,
            BaselineTramitacaoModel.regime_tramitacao == model.regime_tramitacao,
            BaselineTramitacaoModel.fase_codigo == model.fase_codigo,
        )
        existing = self.session.exec(statement).first()

        if existing:
            existing.mediana_dias = model.mediana_dias
            existing.origem_dados = model.origem_dados
            model = existing
        else:
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def buscar_baseline(
        self,
        escopo: str,
        tipo: str | None = None,
        regime_tramitacao: str | None = None,
        fase_codigo: str | None = None,
    ) -> BaselineTramitacao | None:
        """
        Busca um baseline de tramitação com fallbacks na seguinte prioridade:
        1. Busca exata (Tipo + Regime + Fase)
        2. Simplificação (Tipo + Fase, sem Regime)
        3. Global da Fase (sem Tipo e sem Regime)
        """
        # 1. Busca Exata
        statement = select(BaselineTramitacaoModel).where(
            BaselineTramitacaoModel.escopo == escopo,
            BaselineTramitacaoModel.tipo == tipo,
            BaselineTramitacaoModel.regime_tramitacao == regime_tramitacao,
            BaselineTramitacaoModel.fase_codigo == fase_codigo,
        )
        model = self.session.exec(statement).first()
        if model:
            return self._to_entity(model)

        # 2. Primeiro Fallback: Tipo + Fase (sem Regime)
        if regime_tramitacao is not None:
            statement = select(BaselineTramitacaoModel).where(
                BaselineTramitacaoModel.escopo == escopo,
                BaselineTramitacaoModel.tipo == tipo,
                BaselineTramitacaoModel.regime_tramitacao == None,  # noqa: E711
                BaselineTramitacaoModel.fase_codigo == fase_codigo,
            )
            model = self.session.exec(statement).first()
            if model:
                return self._to_entity(model)

        # 3. Segundo Fallback: Global da Fase (sem Tipo e sem Regime)
        if tipo is not None or regime_tramitacao is not None:
            statement = select(BaselineTramitacaoModel).where(
                BaselineTramitacaoModel.escopo == escopo,
                BaselineTramitacaoModel.tipo == None,  # noqa: E711
                BaselineTramitacaoModel.regime_tramitacao == None,  # noqa: E711
                BaselineTramitacaoModel.fase_codigo == fase_codigo,
            )
            model = self.session.exec(statement).first()
            if model:
                return self._to_entity(model)

        return None

    def remover_calculos_dinamicos(self) -> None:
        """Remove todos os cálculos de baseline dinâmicos."""
        statement = select(BaselineTramitacaoModel).where(
            BaselineTramitacaoModel.origem_dados == "DYNAMIC_CALCULATION"
        )
        resultados = self.session.exec(statement).all()
        for r in resultados:
            self.session.delete(r)
        self.session.commit()
