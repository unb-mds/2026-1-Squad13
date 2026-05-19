from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON


class ApensamentoModel(SQLModel, table=True):
    """
    Modelo de persistência para Apensamentos.
    """
    __tablename__ = "apensamento"

    apensamento_id: Optional[int] = Field(default=None, primary_key=True)
    materia_apensada_id: str = Field(foreign_key="proposicao.id", index=True)
    materia_principal_id: str = Field(index=True)
    data_apensacao: str = Field(description="Data em que foi formalizada a apensação")
    casa: str = Field(description="CAMARA ou SENADO")
    fonte_endpoint: Optional[str] = None
    payload_bruto: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    confianca: float = Field(
        default=1.0, description="Score de confiança se detectado por heurística"
    )
