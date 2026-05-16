"""
Entidade central do modelo analítico — substitui a antiga Tramitacao.

Cada registro representa um evento discreto na tramitação de uma proposição,
enriquecido com tipo normalizado, fase analítica e flags de controle.

Mapeamento da Tramitacao antiga:
    id              → evento_id
    proposicao_id   → proposicao_id (FK mantida)
    data_hora       → data_evento
    sequencia       → sequencia
    sigla_orgao     → sigla_orgao
    descricao_tram. → descricao_original
    despacho        → descricao_original (consolidado)
    status          → (removido, substituído por tipo_evento)

Campos novos: tipo_evento, fase_analitica_id, deliberativo,
              mudou_fase, mudou_orgao, remessa_ou_retorno, payload_bruto

Invariantes (validados via __init__):
    - tipo_evento deve ser membro válido de TipoEvento
    - remessa_ou_retorno restrito a None, "REMESSA" ou "RETORNO"
    - sequencia >= 1
    - data_evento em formato ISO (YYYY-MM-DD no mínimo)

Nota técnica: SQLModel com table=True ignora model_validator do Pydantic V2.
Por isso usamos __init__ com super().__init__() + validação explícita.
"""

import re
from typing import Optional

from sqlalchemy import Column, JSON, Index
from sqlmodel import Field, SQLModel


# Regex para validar formato ISO: YYYY-MM-DD com hora opcional
_ISO_DATE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD obrigatório
    r"([T ]\d{2}:\d{2}(:\d{2})?)?$"  # Thh:mm(:ss) opcional
)

_REMESSA_RETORNO_VALIDOS = {None, "REMESSA", "RETORNO"}


class EventoTramitacao(SQLModel, table=True):
    """
    Evento de tramitação legislativa — modelo analítico.

    Cada movimentação de uma proposição gera um EventoTramitacao com:
    - tipo_evento normalizado (enum TipoEvento)
    - fase analítica derivada (FK para fase_analitica)
    - flags booleanos para análise temporal e de transição
    """

    __tablename__ = "evento_tramitacao"
    __table_args__ = (
        Index("ix_evento_tramitacao_prop_data_seq", "proposicao_id", "data_evento", "sequencia"),
    )

    evento_id: Optional[int] = Field(default=None, primary_key=True)
    proposicao_id: str = Field(foreign_key="proposicao.id", index=True)
    data_evento: str
    sequencia: int
    sigla_orgao: Optional[str] = Field(default=None, index=True)
    descricao_original: str

    # Campos analíticos
    tipo_evento: str = Field(
        index=True,
        description="Valor do enum TipoEvento (armazenado como string)",
    )
    fase_analitica_id: Optional[int] = Field(
        default=None,
        foreign_key="fase_analitica.id",
        index=True,
    )

    # Flags de controle analítico
    deliberativo: bool = Field(
        default=False,
        description="True se o evento é uma votação ou decisão",
    )
    mudou_fase: bool = Field(
        default=False,
        description="True se este evento marca transição de fase analítica",
    )
    mudou_orgao: bool = Field(
        default=False,
        description="True se o órgão mudou em relação ao evento anterior",
    )
    remessa_ou_retorno: Optional[str] = Field(
        default=None,
        description="'REMESSA' ou 'RETORNO' quando há trânsito entre Casas",
    )

    # Auditoria
    payload_bruto: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="JSON original da API para rastreabilidade",
    )

    # --- Invariantes via __init__ ---
    # Nota: SQLModel table=True ignora model_validator de Pydantic V2.
    # Usamos __init__ + super().__init__() para garantir validação.

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
            raise ValueError(
                f"sequencia deve ser >= 1, recebido: {self.sequencia}"
            )

        # 4. data_evento em formato ISO
        if not _ISO_DATE_RE.match(self.data_evento):
            raise ValueError(
                f"data_evento deve estar no formato ISO "
                f"(YYYY-MM-DD[Thh:mm[:ss]]), "
                f"recebido: '{self.data_evento}'"
            )

    # --- Properties ---

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
        """Retorna True se o evento representa votação ou decisão.

        Derivado do tipo_evento — documenta a regra de negócio.
        O campo `deliberativo` persistido serve para queries SQL;
        esta property serve para lógica de domínio.
        """
        from domain.entities.tipo_evento import TipoEvento

        deliberativos = {
            TipoEvento.VOTACAO_COMISSAO.value,
            TipoEvento.VOTACAO_PLENARIO.value,
            TipoEvento.APROVACAO.value,
            TipoEvento.REJEICAO.value,
        }
        return self.tipo_evento in deliberativos
