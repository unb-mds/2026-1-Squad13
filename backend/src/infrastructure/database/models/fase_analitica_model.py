from sqlmodel import Field, SQLModel


class FaseAnaliticaModel(SQLModel, table=True):
    """
    Modelo de persistência para Fases Analíticas.
    """

    __tablename__ = "fase_analitica"

    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True)
    nome: str
    ordem_logica: int = Field(index=True)
    natureza: str = Field(default="operacional")
    papel_fluxo: str = Field(default="permanencia")
    permite_estoque_atual: bool = Field(default=True)
    permite_metricas_tempo: bool = Field(default=True)
    indica_fase_terminal: bool = Field(default=False)
    justificativa_juridica: str = Field(default="")
