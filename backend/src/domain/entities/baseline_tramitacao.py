from sqlmodel import SQLModel


class BaselineTramitacao(SQLModel):
    """
    Entidade de Domínio Pura.
    Representa o Baseline de Tramitação (Bootstrap e Dinâmico).
    """

    baseline_id: int | None = None
    escopo: str
    tipo: str | None = None
    regime_tramitacao: str | None = None
    fase_codigo: str | None = None
    mediana_dias: int = 0
    origem_dados: str
