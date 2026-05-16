"""
Funções puras de domínio para classificação de eventos de tramitação.

Nenhuma dependência de infra (sem HTTP, banco, cache).
Usam apenas os enums TipoEvento e FaseCodigo.

- classificar_tipo_evento(): descrição bruta → TipoEvento
- determinar_fase_analitica(): TipoEvento × fase_atual → FaseCodigo
"""

import re
from typing import Optional

from domain.entities.fase_codigo import FaseCodigo
from domain.entities.tipo_evento import TipoEvento

# ---------------------------------------------------------------------------
# Padrões de classificação — ordenados por PRIORIDADE (mais específico primeiro)
#
# Trade-off: a ordem importa. Patterns terminais (PROMULGACAO, SANCAO_OU_VETO)
# vêm antes dos genéricos (RECEBIMENTO_ORGAO, DESPACHO) para evitar que
# "Sancionada e promulgada" case com DESPACHO via substring "despacho" acidental.
#
# Cada tupla: (regex compilado case-insensitive, TipoEvento correspondente)
# ---------------------------------------------------------------------------

_PATTERNS: list[tuple[re.Pattern, TipoEvento]] = [
    # --- Terminais (mais específicos primeiro) ---
    (re.compile(r"promulga", re.IGNORECASE), TipoEvento.PROMULGACAO),
    #
    # ENVIO_EXECUTIVO antes de SANCAO_OU_VETO:
    # "Enviado ao Executivo para sanção" deve casar com ENVIO, não SANCAO.
    (
        re.compile(r"envi.*executivo|remetid.*presid", re.IGNORECASE),
        TipoEvento.ENVIO_EXECUTIVO,
    ),
    (
        re.compile(r"sanciona|veto|sanção|sançao", re.IGNORECASE),
        TipoEvento.SANCAO_OU_VETO,
    ),
    (re.compile(r"prejudicad", re.IGNORECASE), TipoEvento.PREJUDICIALIDADE),
    (re.compile(r"arquiv", re.IGNORECASE), TipoEvento.ARQUIVAMENTO),
    (re.compile(r"rejeit", re.IGNORECASE), TipoEvento.REJEICAO),
    # --- Deliberação ---
    (
        re.compile(r"votaç.*plen[aá]rio|plen[aá]rio.*votaç", re.IGNORECASE),
        TipoEvento.VOTACAO_PLENARIO,
    ),
    (
        re.compile(r"votaç.*comiss|comiss.*votaç", re.IGNORECASE),
        TipoEvento.VOTACAO_COMISSAO,
    ),
    # --- Pauta ---
    (
        re.compile(r"retir.*pauta|pauta.*retir", re.IGNORECASE),
        TipoEvento.RETIRADA_PAUTA,
    ),
    (
        re.compile(
            r"inclu.*pauta|pauta.*inclu|pronta.*pauta",
            re.IGNORECASE,
        ),
        TipoEvento.INCLUSAO_PAUTA,
    ),
    # --- Comissões ---
    # PARECER e DESIGNACAO_RELATOR antes de APROVACAO:
    # "Parecer do relator aprovado" deve casar com PARECER, não APROVACAO.
    (
        re.compile(r"parecer|voto.*relator", re.IGNORECASE),
        TipoEvento.PARECER,
    ),
    (
        re.compile(r"design.*relator|relator.*design", re.IGNORECASE),
        TipoEvento.DESIGNACAO_RELATOR,
    ),
    # APROVACAO depois de PARECER/DESIGNACAO para não capturar
    # "aprovado" em contextos de parecer/relator.
    (re.compile(r"aprovad", re.IGNORECASE), TipoEvento.APROVACAO),
    # --- Trânsito entre Casas ---
    (
        re.compile(
            r"receb.*outra\s*casa|outra\s*casa.*receb",
            re.IGNORECASE,
        ),
        TipoEvento.RECEBIMENTO_OUTRA_CASA,
    ),
    (
        re.compile(
            r"remes.*outra\s*casa|outra\s*casa.*remes"
            r"|enviado.*senado|enviado.*c[aâ]mara"
            r"|remetid.*senado|remetid.*c[aâ]mara",
            re.IGNORECASE,
        ),
        TipoEvento.REMESSA_OUTRA_CASA,
    ),
    (
        re.compile(
            r"retorn.*casa\s*inic|casa\s*inic.*retorn",
            re.IGNORECASE,
        ),
        TipoEvento.RETORNO_INICIADORA,
    ),
    # --- Genéricos (última prioridade antes do fallback) ---
    (
        re.compile(r"receb|encaminhad.*comiss", re.IGNORECASE),
        TipoEvento.RECEBIMENTO_ORGAO,
    ),
    (re.compile(r"despacho|distribu", re.IGNORECASE), TipoEvento.DESPACHO),
    (
        re.compile(r"apresentaç|leitura", re.IGNORECASE),
        TipoEvento.APRESENTACAO,
    ),
]


def classificar_tipo_evento(descricao: str) -> TipoEvento:
    """Classifica uma descrição bruta de tramitação em um TipoEvento.

    Recebe a descrição original vinda da API da Câmara ou Senado e retorna
    o TipoEvento correspondente baseado em padrões regex ordenados por
    prioridade.

    Args:
        descricao: texto bruto da movimentação (descricao_tramitacao ou
                   despacho da API).

    Returns:
        TipoEvento correspondente, ou NAO_CLASSIFICADO se nenhum pattern casar.

    Raises:
        TypeError: se descricao não for string.

    Exemplos:
        >>> classificar_tipo_evento("Apresentação do projeto")
        <TipoEvento.APRESENTACAO: 'APRESENTACAO'>
        >>> classificar_tipo_evento("texto desconhecido xyz")
        <TipoEvento.NAO_CLASSIFICADO: 'NAO_CLASSIFICADO'>
    """
    if not isinstance(descricao, str):
        raise TypeError(
            f"descricao deve ser str, recebido: {type(descricao).__name__}"
        )

    texto = descricao.strip()
    if not texto:
        return TipoEvento.NAO_CLASSIFICADO

    for pattern, tipo in _PATTERNS:
        if pattern.search(texto):
            return tipo

    return TipoEvento.NAO_CLASSIFICADO


# ---------------------------------------------------------------------------
# Mapeamento TipoEvento → FaseCodigo
#
# Regras especiais:
#   - APROVACAO: nunca muda fase sozinha (a fase muda com o evento seguinte)
#   - NAO_CLASSIFICADO: nunca muda fase
#   - RETORNO_INICIADORA: regride para ANALISE_COMISSOES
# ---------------------------------------------------------------------------

_TIPO_PARA_FASE: dict[TipoEvento, FaseCodigo] = {
    TipoEvento.APRESENTACAO: FaseCodigo.PROTOCOLO_INICIAL,
    TipoEvento.DESPACHO: FaseCodigo.PROTOCOLO_INICIAL,
    TipoEvento.RECEBIMENTO_ORGAO: FaseCodigo.ANALISE_COMISSOES,
    TipoEvento.DESIGNACAO_RELATOR: FaseCodigo.ANALISE_COMISSOES,
    TipoEvento.PARECER: FaseCodigo.ANALISE_COMISSOES,
    TipoEvento.VOTACAO_COMISSAO: FaseCodigo.ANALISE_COMISSOES,
    TipoEvento.INCLUSAO_PAUTA: FaseCodigo.AGUARDANDO_PAUTA,
    TipoEvento.RETIRADA_PAUTA: FaseCodigo.AGUARDANDO_PAUTA,
    TipoEvento.VOTACAO_PLENARIO: FaseCodigo.DELIBERACAO_PLENARIO,
    TipoEvento.REMESSA_OUTRA_CASA: FaseCodigo.TRAMITE_ENTRE_CASAS,
    TipoEvento.RECEBIMENTO_OUTRA_CASA: FaseCodigo.REVISAO_OUTRA_CASA,
    TipoEvento.RETORNO_INICIADORA: FaseCodigo.ANALISE_COMISSOES,
    TipoEvento.ENVIO_EXECUTIVO: FaseCodigo.ETAPA_EXECUTIVO,
    TipoEvento.SANCAO_OU_VETO: FaseCodigo.ENCERRADA,
    TipoEvento.PROMULGACAO: FaseCodigo.ENCERRADA,
    TipoEvento.ARQUIVAMENTO: FaseCodigo.ENCERRADA,
    TipoEvento.PREJUDICIALIDADE: FaseCodigo.ENCERRADA,
    TipoEvento.REJEICAO: FaseCodigo.ENCERRADA,
    # APROVACAO e NAO_CLASSIFICADO NÃO estão no mapeamento
    # porque possuem lógica especial (ver determinar_fase_analitica)
}

# Fallback quando fase_atual é None e o evento não determina fase
_FASE_FALLBACK = FaseCodigo.PROTOCOLO_INICIAL


def determinar_fase_analitica(
    tipo_evento: TipoEvento,
    fase_atual: Optional[FaseCodigo],
) -> FaseCodigo:
    """Determina a fase analítica resultante de um evento.

    Mapeamento determinístico de TipoEvento para FaseCodigo, com
    tratamento especial para APROVACAO e NAO_CLASSIFICADO.

    Args:
        tipo_evento: tipo normalizado do evento.
        fase_atual: fase em que a proposição se encontra antes deste
                    evento. None para o primeiro evento da proposição.

    Returns:
        FaseCodigo resultante após o evento.

    Regras especiais:
        - APROVACAO: nunca muda fase sozinha. A transição real vem do
          evento seguinte (REMESSA_OUTRA_CASA ou ENVIO_EXECUTIVO).
        - NAO_CLASSIFICADO: nunca altera fase. Se fase_atual for None,
          retorna PROTOCOLO_INICIAL como fallback seguro.
        - RETORNO_INICIADORA: regride para ANALISE_COMISSOES.
    """
    # NAO_CLASSIFICADO: mantém a fase atual, jamais altera
    if tipo_evento == TipoEvento.NAO_CLASSIFICADO:
        return fase_atual if fase_atual is not None else _FASE_FALLBACK

    # APROVACAO: não muda fase sozinha
    if tipo_evento == TipoEvento.APROVACAO:
        return fase_atual if fase_atual is not None else _FASE_FALLBACK

    # Mapeamento direto para todos os outros tipos
    fase_determinada = _TIPO_PARA_FASE.get(tipo_evento)

    if fase_determinada is not None:
        return fase_determinada

    # Safety net: tipo desconhecido não deveria chegar aqui,
    # mas caso chegue, mantém fase atual
    return fase_atual if fase_atual is not None else _FASE_FALLBACK
