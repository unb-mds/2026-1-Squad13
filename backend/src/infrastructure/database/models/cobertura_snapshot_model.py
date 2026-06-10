from datetime import datetime

from sqlmodel import Field, SQLModel


class CoberturaSnapshotModel(SQLModel, table=True):
    """
    Modelo de persistência para snapshots de cobertura analítica.
    """

    __tablename__ = "cobertura_snapshot"

    id: int | None = Field(default=None, primary_key=True)
    ano: int = Field(index=True)
    tipo_proposicao: str = Field(index=True)
    total_api_oficial: int
    data_atualizacao: datetime = Field(default_factory=datetime.utcnow)
