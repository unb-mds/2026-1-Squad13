import re
from typing import Optional
from sqlmodel import SQLModel

# Regex para validar formato ISO: YYYY-MM-DD com hora opcional
_ISO_DATE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD obrigatório
    r"([T ]\d{2}:\d{2}(:\d{2})?)?$"  # Thh:mm(:ss) opcional
)

_REMESSA_RETORNO_VALIDOS = {None, "REMESSA", "RETORNO"}


class EventoTramitacao(SQLModel):
    """
    Evento de tramitação legislativa — entidade de domínio pura.
    """

    evento_id: Optional[int] = None
    proposicao_id: str
    data_evento: str
    sequencia: int
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

    def __init__(self, **data):
        super().__init__(**data)
        self._validar_invariantes()

    def _validar_invariantes(self):
        """Valida regras de negócio na criação do evento."""
        from domain.entities.tipo_evento import TipoEvento

        # 1. tipo_evento deve ser membro válido do enum
        valores_validos = {membro.value for membro in TipoEvento}
        if self.tipo_evento not in valores_validos:
            raise ValueError(
                f"tipo_evento '{self.tipo_evento}' não é membro de TipoEvento. "
                f"Valores válidos: {sorted(valores_validos)}"
            )

        # 2. remessa_ou_retorno restrito
        if self.remessa_ou_retorno not in _REMESSA_RETORNO_VALIDOS:
            raise ValueError(
                f"remessa_ou_retorno deve ser None, 'REMESSA' ou 'RETORNO', "
                f"recebido: '{self.remessa_ou_retorno}'"
            )

        # 3. sequencia >= 1
        if self.sequencia < 1:
            raise ValueError(f"sequencia deve ser >= 1, recebido: {self.sequencia}")

        # 4. data_evento em formato ISO
        if not _ISO_DATE_RE.match(self.data_evento):
            raise ValueError(
                f"data_evento deve estar no formato ISO "
                f"(YYYY-MM-DD[Thh:mm[:ss]]), "
                f"recebido: '{self.data_evento}'"
            )

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
