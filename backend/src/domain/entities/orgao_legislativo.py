from enum import Enum
from typing import Optional

from sqlmodel import SQLModel


class CasaLegislativa(str, Enum):
    """Casa legislativa a que o órgão pertence."""

    CAMARA = "CAMARA"
    SENADO = "SENADO"
    AMBAS = "AMBAS"


class OrgaoLegislativo(SQLModel):
    """
    Entidade de Domínio Pura para Órgão Legislativo.
    """

    id: Optional[int] = None
    sigla: str
    nome: Optional[str] = None
    casa: CasaLegislativa
    id_origem: Optional[str] = None


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
