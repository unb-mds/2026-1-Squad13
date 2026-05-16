"""
Cadastro normalizado de órgãos legislativos (comissões, plenário, mesa).

Estratégia de persistência: upsert automático.
Os adapters criam/atualizam órgãos conforme encontram novas siglas nas APIs.

Chave de upsert: (id_origem, casa) quando disponível, com fallback (sigla, casa).
Isso evita duplicatas quando um órgão é recriado com novo ID entre legislaturas.

Seed fixo mínimo: apenas para órgãos implícitos que os adapters nunca retornam
explicitamente (PLEN, MESA, SECCJ).
"""

from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class CasaLegislativa(str, Enum):
    """Casa legislativa a que o órgão pertence."""

    CAMARA = "CAMARA"
    SENADO = "SENADO"
    AMBAS = "AMBAS"


class OrgaoLegislativo(SQLModel, table=True):
    """
    Órgão legislativo normalizado.

    Representa comissões permanentes, temporárias, plenário e mesa diretora.
    Criado automaticamente via upsert pelos adapters.
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
