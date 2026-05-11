from sqlmodel import SQLModel, Field
from typing import Optional, List, Any
from sqlalchemy import Column, JSON

class Proposicao(SQLModel, table=True):
    """
    Entidade de Domínio e Modelo de Banco de Dados.
    Representa uma Proposição Legislativa (PL, PEC, etc).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: str
    numero: int
    ano: int
    autor: str
    uf_autor: str
    status_tramitacao: str
    ementa: str
    data_apresentacao: str
    data_ultima_movimentacao: str
    orgao_atual: str
    link_oficial: Optional[str] = None
    
    # Armazenar lista como JSON no Postgres
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    @property
    def nome_canonico(self) -> str:
        """Exemplo: PL 123/2024"""
        return f"{self.tipo} {self.numero}/{self.ano}"
