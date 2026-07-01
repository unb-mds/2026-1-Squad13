from datetime import date

from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class PeriodoFaseModel(SQLModel, table=True):
    """
    Modelo de persistência para os Períodos de Fase (periodo_fase).
    """

    __tablename__ = "periodo_fase"

    __table_args__ = (
        Index("idx_periodo_proposicao_atual", "proposicao_id", "eh_fase_atual"),
        Index(
            "idx_periodo_analise_dashboard",
            "fase_analitica_id",
            "rito",
            "tipo_proposicao",
            postgresql_where="eh_fase_atual = TRUE",
        ),
        Index("idx_periodo_cronologia", "data_inicio", "data_fim"),
    )

    id: int | None = Field(default=None, primary_key=True)
    proposicao_id: str = Field(foreign_key="proposicao.id", index=True)
    fase_analitica_id: int = Field(foreign_key="fase_analitica.id", index=True)
    data_inicio: date = Field(index=True)
    data_fim: date | None = Field(default=None, index=True)
    duracao_dias: int | None = Field(default=None)
    recorrencia_numero: int = Field(default=1)
    eh_fase_atual: bool = Field(default=False, index=True)
    motivo_travamento: str | None = Field(default=None, nullable=True)
    tipo_proposicao: str = Field(index=True)
    rito: str = Field(index=True)
    numero_turno: int | None = Field(default=None, nullable=True)
    subtipo_fase: str | None = Field(default=None, nullable=True)
    tipo_sessao: str | None = Field(default=None, nullable=True)
    origem_calculo: str
