from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel


class CasaLegislativa(str, Enum):
    """Casa legislativa a que o órgão pertence."""
    CAMARA = "CAMARA"
    SENADO = "SENADO"
    AMBAS = "AMBAS"


class OrgaoLegislativoModel(SQLModel, table=True):
    """
    Modelo de persistência para Órgãos Legislativos.
    """
    __tablename__ = "orgaolegislativo"

    id: Optional[int] = Field(default=None, primary_key=True)
    sigla: str = Field(index=True)
    nome: Optional[str] = None
    casa: CasaLegislativa
    id_origem: Optional[str] = Field(
        default=None,
        index=True,
        description="ID do órgão na API de origem (Câmara ou Senado)",
        )