"""
Enum puro dos códigos de fase analítica do processo legislativo.

Existe paralelamente à tabela FaseAnalitica (SQLModel, table=True) que
vive em fase_analitica.py. A tabela é responsabilidade da camada de infra;
este enum é para uso exclusivo nas funções de domínio, garantindo
type-safety sem dependência de banco.

As 8 fases seguem a ordem lógica definida no MIGRATION_SCOPE.md.
"""

from enum import Enum


class FaseCodigo(str, Enum):
    """
    8 códigos canônicos do ciclo de vida legislativo.

    Herda de str para comparação direta com os valores de
    FaseAnalitica.codigo (persistidos como string).

    A ordem dos membros reflete a progressão lógica —
    proposições podem regredir (ex: RETORNO_INICIADORA
    faz voltar de REVISAO_OUTRA_CASA para ANALISE_COMISSOES).
    """

    PROTOCOLO_INICIAL = "PROTOCOLO_INICIAL"        # ordem 1
    ANALISE_COMISSOES = "ANALISE_COMISSOES"         # ordem 2
    AGUARDANDO_PAUTA = "AGUARDANDO_PAUTA"           # ordem 3
    DELIBERACAO_PLENARIO = "DELIBERACAO_PLENARIO"   # ordem 4
    TRAMITE_ENTRE_CASAS = "TRAMITE_ENTRE_CASAS"     # ordem 5
    REVISAO_OUTRA_CASA = "REVISAO_OUTRA_CASA"       # ordem 6
    ETAPA_EXECUTIVO = "ETAPA_EXECUTIVO"             # ordem 7
    ENCERRADA = "ENCERRADA"                         # ordem 8
