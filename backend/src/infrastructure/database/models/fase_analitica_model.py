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
