from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import field_validator

# Regex para validar formato ISO: YYYY-MM-DD com hora opcional
_ISO_DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?)?$"

_REMESSA_RETORNO_VALIDOS = {None, "REMESSA", "RETORNO"}


class EventoTramitacao(SQLModel):
    """
    Evento de tramitação legislativa — entidade de domínio pura.
    """

    evento_id: Optional[int] = None
    proposicao_id: str
    data_evento: str = Field(pattern=_ISO_DATE_PATTERN)
    sequencia: int = Field(ge=1)
    sigla_orgao: Optional[str] = None
    descricao_original: str

    # Campos analíticos
    tipo_evento: str
    fase_analitica_id: Optional[int] = None

    # Flags de controle analítico
    deliberativo: bool = False
    mudou_fase: bool = False
    mudou_orgao: bool = False
    remessa_ou_retorno: Optional[str] = None

    # Campos de análise temporal
    dias_na_etapa: int = 0
    tem_atraso: bool = False
    marca_apensacao: bool = False

    # Auditoria
    payload_bruto: Optional[dict] = None

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
    def validar_remessa_ou_retorno(cls, v: Optional[str]) -> Optional[str]:
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
