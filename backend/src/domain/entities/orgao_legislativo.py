from enum import StrEnum

from sqlmodel import SQLModel


class CasaLegislativa(StrEnum):
    """Casa legislativa a que o órgão pertence."""

    CAMARA = "CAMARA"
    SENADO = "SENADO"
    AMBAS = "AMBAS"


class OrgaoLegislativo(SQLModel):
    """
    Entidade de Domínio Pura para Órgão Legislativo.
    """

    id: int | None = None
    sigla: str
    nome: str | None = None
    casa: CasaLegislativa
    id_origem: str | None = None


# Seed mínimo para órgãos implícitos
ORGAOS_SEED = [
    {
        "sigla": "PLEN",
        "nome": "Plenário",
        "casa": CasaLegislativa.AMBAS,
    },
    {
        "sigla": "MESA",
        "nome": "Mesa Diretora",
        "casa": CasaLegislativa.AMBAS,
    },
    {
        "sigla": "SECCJ",
        "nome": "Secretaria de Comissões (Justiça)",
        "casa": CasaLegislativa.AMBAS,
    },
]
