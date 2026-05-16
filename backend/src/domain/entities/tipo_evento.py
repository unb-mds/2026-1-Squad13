"""
Enum dos tipos de evento normalizados para tramitação legislativa.

Cada evento bruto vindo das APIs da Câmara ou Senado é classificado em
exatamente um destes 20 tipos pela função classificar_tipo_evento().

NAO_CLASSIFICADO é o fallback — nunca altera a fase analítica da
proposição. Isso permite medir a taxa de cobertura do classificador
sem contaminar métricas de tempo por fase.
"""

from enum import Enum


class TipoEvento(str, Enum):
    """
    20 tipos normalizados de evento de tramitação.

    Herda de str para serialização automática em JSON/SQLModel.
    """

    # --- Início do ciclo ---
    APRESENTACAO = "APRESENTACAO"
    DESPACHO = "DESPACHO"

    # --- Tramitação em comissões ---
    RECEBIMENTO_ORGAO = "RECEBIMENTO_ORGAO"
    DESIGNACAO_RELATOR = "DESIGNACAO_RELATOR"
    PARECER = "PARECER"

    # --- Pauta e deliberação ---
    INCLUSAO_PAUTA = "INCLUSAO_PAUTA"
    RETIRADA_PAUTA = "RETIRADA_PAUTA"
    VOTACAO_COMISSAO = "VOTACAO_COMISSAO"
    VOTACAO_PLENARIO = "VOTACAO_PLENARIO"

    # --- Resultados ---
    APROVACAO = "APROVACAO"
    REJEICAO = "REJEICAO"

    # --- Trânsito entre Casas ---
    REMESSA_OUTRA_CASA = "REMESSA_OUTRA_CASA"
    RECEBIMENTO_OUTRA_CASA = "RECEBIMENTO_OUTRA_CASA"
    RETORNO_INICIADORA = "RETORNO_INICIADORA"

    # --- Encerramento ---
    ARQUIVAMENTO = "ARQUIVAMENTO"
    PREJUDICIALIDADE = "PREJUDICIALIDADE"

    # --- Etapa executiva ---
    ENVIO_EXECUTIVO = "ENVIO_EXECUTIVO"
    SANCAO_OU_VETO = "SANCAO_OU_VETO"
    PROMULGACAO = "PROMULGACAO"

    # --- Fallback ---
    NAO_CLASSIFICADO = "NAO_CLASSIFICADO"
