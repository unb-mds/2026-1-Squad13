from sqlmodel import SQLModel, Field
from typing import Optional, List
from sqlalchemy import Column, JSON

class Proposicao(SQLModel, table=True):
    """
    Entidade de Domínio e Modelo de Banco de Dados.
    Representa uma Proposição Legislativa (PL, PEC, etc).
    Combina a estrutura robusta da 'main' com a persistência da 'develop'.
    """
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
    
    # Armazenar lista como JSON no Postgres
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    @property
    def nome_canonico(self) -> str:
        """Exemplo: PL 123/2024"""
        return f"{self.tipo} {self.numero}/{self.ano}"
