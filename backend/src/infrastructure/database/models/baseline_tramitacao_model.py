from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint


class BaselineTramitacaoModel(SQLModel, table=True):
    """
    Modelo de persistência para as métricas de Baseline de Tramitação (Bootstrap e Dinâmico).
    """

    __tablename__ = "baseline_tramitacao"

    baseline_id: int | None = Field(default=None, primary_key=True)
    escopo: str = Field(index=True, description="TOTAL (para IAR) ou FASE (para IAF)")
    tipo: str | None = Field(
        default=None, index=True, description="Ex: 'PL', 'PEC', 'MPV'"
    )
    regime_tramitacao: str | None = Field(
        default=None, index=True, description="Ex: 'ORDINARIO', 'URGENCIA'"
    )
    fase_codigo: str | None = Field(
        default=None, index=True, description="Código da fase (nulo se escopo for TOTAL)"
    )
    mediana_dias: int = Field(default=0, description="O valor de referência em dias")
    origem_dados: str = Field(
        index=True, description="DYNAMIC_CALCULATION ou BOOTSTRAP_SEED"
    )

    __table_args__ = (
        UniqueConstraint(
            "escopo",
            "tipo",
            "regime_tramitacao",
            "fase_codigo",
            name="uq_baseline_tramitacao_escopo_tipo_regime_fase",
            postgresql_nulls_not_distinct=True,
        ),
    )
