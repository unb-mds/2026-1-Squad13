from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON


class Apensamento(SQLModel, table=True):
    """
    Representa a relação de apensamento entre duas proposições.
    Conforme especificação: junção formal da tramitação de uma apensada à principal.
    """

    __tablename__ = "apensamento"

    apensamento_id: Optional[int] = Field(default=None, primary_key=True)
    materia_apensada_id: str = Field(foreign_key="proposicao.id", index=True)
    materia_principal_id: str = Field(index=True)  # Pode não estar no nosso banco ainda
    data_apensacao: str = Field(description="Data em que foi formalizada a apensação")
    casa: str = Field(description="CAMARA ou SENADO")
    fonte_endpoint: Optional[str] = None
    payload_bruto: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    confianca: float = Field(
        default=1.0, description="Score de confiança se detectado por heurística"
    )
