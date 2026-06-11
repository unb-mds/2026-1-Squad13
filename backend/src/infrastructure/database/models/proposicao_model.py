from sqlmodel import SQLModel, Field
from typing import Optional, List
from sqlalchemy import Column, JSON
from sqlalchemy.dialects import postgresql


class ProposicaoModel(SQLModel, table=True):
    """
    Modelo de persistência para Proposições Legislativas.
    Separado da entidade de domínio para respeitar a Layered Architecture.
    """

    __tablename__ = "proposicao"

    id: Optional[str] = Field(default=None, primary_key=True)
    tipo: str
    numero: str
    ano: int
    ementa: str
    ementa_resumida: Optional[str] = None
    autor: str
    uf_autor: Optional[str] = None
    orgao_origem: Optional[str] = None
    status: str
    orgao_atual: str
    data_apresentacao: str
    data_ultima_movimentacao: str
    tempo_total_dias: Optional[int] = 0
    tem_atraso: Optional[bool] = False
    tem_previsao_ia: Optional[bool] = False
    link_oficial: Optional[str] = None
    data_encerramento: Optional[str] = None
    previsao_aprovacao_dias: Optional[int] = None
    numero_emendas: Optional[int] = 0

    # Armazenar lista como JSONB no Postgres para busca eficiente (@>),
    # mas mantendo JSON genérico para compatibilidade com SQLite nos testes.
    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON().with_variant(postgresql.JSONB(), "postgresql")),
    )
