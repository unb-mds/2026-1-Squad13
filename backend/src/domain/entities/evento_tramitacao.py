import re

from pydantic import field_validator
from sqlmodel import SQLModel

from domain.entities.tipo_evento import TipoEvento

# Regex para validar formato ISO: YYYY-MM-DD com hora opcional
_ISO_DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?)?$"

_REMESSA_RETORNO_VALIDOS = {None, "REMESSA", "RETORNO"}

TIPOS_SEMPRE_RELEVANTES = {
    TipoEvento.APRESENTACAO.value,
    TipoEvento.RECEBIMENTO_ORGAO.value,
    TipoEvento.DESIGNACAO_RELATOR.value,
    TipoEvento.VOTACAO_PLENARIO.value,
    TipoEvento.VOTACAO_COMISSAO.value,
    TipoEvento.APROVACAO.value,
    TipoEvento.REJEICAO.value,
    TipoEvento.REMESSA_OUTRA_CASA.value,
    TipoEvento.RECEBIMENTO_OUTRA_CASA.value,
    TipoEvento.RETORNO_INICIADORA.value,
    TipoEvento.SANCAO_OU_VETO.value,
    TipoEvento.ARQUIVAMENTO.value,
    TipoEvento.PREJUDICIALIDADE.value,
    TipoEvento.PROMULGACAO.value,
}


class EventoTramitacao(SQLModel):
    """
    Evento de tramitação legislativa — entidade de domínio pura.
    """

    evento_id: int | None = None
    proposicao_id: str
    data_evento: str
    sequencia: int
    sigla_orgao: str | None = None
    descricao_original: str

    # Campos analíticos
    tipo_evento: str
    fase_analitica_id: int | None = None

    # Flags de controle analítico
    deliberativo: bool = False
    mudou_fase: bool = False
    mudou_orgao: bool = False
    remessa_ou_retorno: str | None = None

    # Campos de análise temporal
    dias_na_etapa: int = 0
    tem_atraso: bool = False
    marca_apensacao: bool = False
    relevante: bool = False

    # Auditoria
    payload_bruto: dict | None = None

    @field_validator("data_evento")
    @classmethod
    def validar_data_evento(cls, v: str) -> str:
        if not re.match(_ISO_DATE_PATTERN, v):
            raise ValueError(
                f"data_evento deve estar no formato ISO "
                f"(YYYY-MM-DD[Thh:mm[:ss]]), "
                f"recebido: '{v}'"
            )
        return v

    @field_validator("sequencia")
    @classmethod
    def validar_sequencia(cls, v: int) -> int:
        if v < 1:
            raise ValueError(f"sequencia deve ser >= 1, recebido: {v}")
        return v

    @field_validator("tipo_evento")
    @classmethod
    def validar_tipo_evento(cls, v: str) -> str:
        from domain.entities.tipo_evento import TipoEvento

        valores_validos = {membro.value for membro in TipoEvento}
        if v not in valores_validos:
            raise ValueError(
                f"tipo_evento '{v}' não é membro de TipoEvento. "
                f"Valores válidos: {sorted(valores_validos)}"
            )
        return v

    @field_validator("remessa_ou_retorno")
    @classmethod
    def validar_remessa_ou_retorno(cls, v: str | None) -> str | None:
        if v not in _REMESSA_RETORNO_VALIDOS:
            raise ValueError(
                f"remessa_ou_retorno deve ser None, 'REMESSA' ou 'RETORNO', "
                f"recebido: '{v}'"
            )
        return v

    @property
    def data_formatada(self) -> str:
        """Retorna apenas a data em formato YYYY-MM-DD."""
        return self.data_evento[:10] if self.data_evento else ""

    @property
    def eh_evento_terminal(self) -> bool:
        """Retorna True se o evento representa um encerramento do trâmite."""
        from domain.entities.tipo_evento import TipoEvento

        terminais = {
            TipoEvento.ARQUIVAMENTO.value,
            TipoEvento.PREJUDICIALIDADE.value,
            TipoEvento.SANCAO_OU_VETO.value,
            TipoEvento.PROMULGACAO.value,
            TipoEvento.REJEICAO.value,
        }
        return self.tipo_evento in terminais

    @property
    def eh_deliberativo(self) -> bool:
        """Retorna True se o evento representa votação ou decisão."""
        from domain.entities.tipo_evento import TipoEvento

        deliberativos = {
            TipoEvento.VOTACAO_COMISSAO.value,
            TipoEvento.VOTACAO_PLENARIO.value,
            TipoEvento.APROVACAO.value,
            TipoEvento.REJEICAO.value,
        }
        return self.tipo_evento in deliberativos

    @property
    def eh_relevante(self) -> bool:
        """
        Regra de negócio para definir se um evento deve ser exibido em visões resumidas.
        """
        return (
            self.tipo_evento in TIPOS_SEMPRE_RELEVANTES
            or self.mudou_fase
            or self.deliberativo
            or (self.dias_na_etapa is not None and self.dias_na_etapa > 30)
            or self.marca_apensacao
        )


def calcular_tempo_por_fase(eventos: list[EventoTramitacao]) -> list[dict]:
    """
    Calcula o breakdown de tempo por fase a partir dos eventos reais.
    Exige no mínimo 2 tramitações para gerar os dados.
    """
    if len(eventos) < 2:
        return []

    from datetime import datetime

    ordenadas = sorted(eventos, key=lambda e: (e.data_evento, e.sequencia))
    tempos: dict[str, int] = {}

    for i in range(len(ordenadas) - 1):
        atual = ordenadas[i]
        proxima = ordenadas[i + 1]

        fase = atual.sigla_orgao or "Outros"

        try:
            d_atual = datetime.fromisoformat(atual.data_evento[:10]).date()
            d_prox = datetime.fromisoformat(proxima.data_evento[:10]).date()
            dias = max(0, (d_prox - d_atual).days)
            tempos[fase] = tempos.get(fase, 0) + dias
        except ValueError:
            continue

    resultado = [{"fase": k, "dias": v} for k, v in tempos.items()]
    return sorted(resultado, key=lambda x: x["dias"], reverse=True)
