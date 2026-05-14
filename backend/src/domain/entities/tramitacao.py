from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class Tramitacao(SQLModel, table=True):
    """
    Representa uma movimentação ou tramitação de uma proposição.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    proposicao_id: str = Field(foreign_key="proposicao.id", index=True)
    data_hora: str
    sequencia: int
    sigla_orgao: str
    descricao_orgao: Optional[str] = None
    descricao_tramitacao: str
    despacho: Optional[str] = None
    status: Optional[str] = None

    @property
    def data_formatada(self) -> str:
        """Retorna apenas a data em formato YYYY-MM-DD."""
        return self.data_hora[:10]
