"""
Lookup das fases analíticas do processo legislativo.

São 8 fases fixas, inseridas no seed antes de qualquer proposição.
Nunca são criadas em runtime — representam o ciclo de vida canônico.

A ordem lógica permite calcular progressão e regressão de uma
proposição entre fases (ex: uma PEC que volta de REVISAO_OUTRA_CASA
para ANALISE_COMISSOES regrediu 4 posições).
"""

from typing import Optional

from sqlmodel import Field, SQLModel


class FaseAnalitica(SQLModel, table=True):
    """
    Fase analítica do processo legislativo.

    Cada EventoTramitacao aponta para exatamente uma fase.
    As 8 fases formam uma sequência lógica, embora o trâmite real
    nem sempre siga essa ordem linear.
    """

    __tablename__ = "fase_analitica"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True)
    nome: str
    ordem_logica: int = Field(index=True)


# Constantes para uso interno — evita strings mágicas no código
FASES_SEED = [
    {"codigo": "PROTOCOLO_INICIAL", "nome": "Protocolo inicial", "ordem_logica": 1},
    {"codigo": "ANALISE_COMISSOES", "nome": "Análise em comissões", "ordem_logica": 2},
    {"codigo": "AGUARDANDO_PAUTA", "nome": "Aguardando pauta", "ordem_logica": 3},
    {
        "codigo": "DELIBERACAO_PLENARIO",
        "nome": "Deliberação em plenário",
        "ordem_logica": 4,
    },
    {
        "codigo": "TRAMITE_ENTRE_CASAS",
        "nome": "Trâmite entre Casas",
        "ordem_logica": 5,
    },
    {
        "codigo": "REVISAO_OUTRA_CASA",
        "nome": "Revisão na outra Casa",
        "ordem_logica": 6,
    },
    {"codigo": "ETAPA_EXECUTIVO", "nome": "Etapa no Executivo", "ordem_logica": 7},
    {"codigo": "ENCERRADA", "nome": "Encerrada", "ordem_logica": 8},
]
