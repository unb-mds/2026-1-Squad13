
from sqlalchemy import JSON, Column, Index
from sqlmodel import Field, SQLModel


class EventoTramitacaoModel(SQLModel, table=True):
    """
    Modelo de persistência para Eventos de Tramitação.
    """

    __tablename__ = "evento_tramitacao"
    __table_args__ = (
        Index(
            "ix_evento_tramitacao_prop_data_seq",
            "proposicao_id",
            "data_evento",
            "sequencia",
        ),
    )

    evento_id: int | None = Field(default=None, primary_key=True)
    proposicao_id: str = Field(foreign_key="proposicao.id", index=True)
    data_evento: str
    sequencia: int
    sigla_orgao: str | None = Field(default=None, index=True)
    descricao_original: str

    # Campos analíticos
    tipo_evento: str = Field(
        index=True,
        description="Valor do enum TipoEvento (armazenado como string)",
    )
    fase_analitica_id: int | None = Field(
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
    remessa_ou_retorno: str | None = Field(
        default=None,
        description="'REMESSA' ou 'RETORNO' when there's transit between Houses",
    )

    # Campos de análise temporal
    dias_na_etapa: int = Field(
        default=0,
        description="Dias decorridos entre este evento e o próximo (ou hoje)",
    )
    tem_atraso: bool = Field(
        default=False,
        description="True se o tempo de permanência nesta etapa ultrapassa o limite esperado",
    )
    marca_apensacao: bool = Field(
        default=False,
        description="Indica se este evento criou uma ligação de apensamento",
    )

    relevante: bool = Field(
        default=False,
        description="Indica se o evento é considerado relevante para visões resumidas",
    )

    # Auditoria
    payload_bruto: dict | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="JSON original da API para rastreabilidade",
    )
