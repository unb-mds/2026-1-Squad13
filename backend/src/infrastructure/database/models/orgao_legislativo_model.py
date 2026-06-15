from enum import StrEnum

from sqlmodel import Field, SQLModel


class CasaLegislativa(StrEnum):
    """Casa legislativa a que o órgão pertence."""

    CAMARA = "CAMARA"
    SENADO = "SENADO"
    AMBAS = "AMBAS"


class OrgaoLegislativoModel(SQLModel, table=True):
    """
    Modelo de persistência para Órgãos Legislativos.
    """

    __tablename__ = "orgaolegislativo"

    id: int | None = Field(default=None, primary_key=True)
    sigla: str = Field(index=True)
    nome: str | None = None
    casa: CasaLegislativa
    id_origem: str | None = Field(
        default=None,
        index=True,
        description="ID do órgão na API de origem (Câmara ou Senado)",
    )
