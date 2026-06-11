from datetime import datetime

from sqlmodel import SQLModel


class CoberturaSnapshot(SQLModel):
    """
    Entidade de Domínio Pura para snapshots de cobertura analítica.
    """

    id: int | None = None
    ano: int
    tipo_proposicao: str
    total_api_oficial: int
    data_atualizacao: datetime
