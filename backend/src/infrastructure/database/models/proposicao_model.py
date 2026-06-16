from datetime import datetime

from pydantic import ConfigDict, field_validator
from sqlalchemy import JSON, Column
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, SQLModel


class ProposicaoModel(SQLModel, table=True):
    """
    Modelo de persistência para Proposições Legislativas.
    Separado da entidade de domínio para respeitar a Layered Architecture.
    """

    __tablename__ = "proposicao"

    model_config = ConfigDict(validate_assignment=True)

    id: str | None = Field(default=None, primary_key=True)
    tipo: str
    numero: str
    ano: int
    ementa: str
    ementa_resumida: str | None = None
    autor: str
    uf_autor: str | None = None
    orgao_origem: str | None = None
    status: str
    status_original: str | None = Field(default=None, nullable=True)
    orgao_atual: str
    data_apresentacao: str
    data_ultima_movimentacao: str
    tempo_total_dias: int | None = 0
    tem_atraso: bool | None = False
    tem_previsao_ia: bool | None = False
    link_oficial: str | None = None
    data_encerramento: str | None = None
    previsao_aprovacao_dias: int | None = None

    # Métricas de atraso e status persistidos
    indice_atraso_relativo: float | None = Field(default=None, nullable=True)
    indice_atraso_fase_atual: float | None = Field(default=None, nullable=True)
    indice_espera_improdutiva: float | None = Field(default=None, nullable=True)
    status_atraso: str | None = Field(default=None, nullable=True)
    dias_decorridos_total: int | None = Field(default=None, nullable=True)
    dias_esperados_total: int | None = Field(default=None, nullable=True)
    baseline_grupo_id: str | None = Field(default=None, nullable=True)
    data_calculo_metricas: datetime | None = Field(default=None, nullable=True)
    regime_tramitacao: str | None = Field(default=None, nullable=True)

    # ML predictive variables
    numero_assinaturas: int | None = Field(default=0, nullable=True)
    numero_emendas: int | None = Field(default=None, nullable=True)
    autor_e_poder_executivo: bool | None = Field(default=False, nullable=True)
    tema_economico: bool | None = Field(default=False, nullable=True)
    bloco_legislativo: str | None = Field(default=None, nullable=True)
    parecer_ccj_favoravel: bool | None = Field(default=None, nullable=True)

    @field_validator("numero_assinaturas")
    @classmethod
    def validar_numero_assinaturas(cls, v):
        if v is not None and v < 0:
            return 0
        return v

    # Armazenar lista como JSONB no Postgres para busca eficiente (@>),
    # mas mantendo JSON genérico para compatibilidade com SQLite nos testes.
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON().with_variant(postgresql.JSONB(), "postgresql")),
    )
