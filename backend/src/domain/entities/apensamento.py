from typing import Optional

from sqlmodel import SQLModel


class Apensamento(SQLModel):
    """
    Entidade de Domínio Pura para Apensamento.
    """

    apensamento_id: Optional[int] = None
    materia_apensada_id: str
    materia_principal_id: str
    data_apensacao: str
    casa: str
    fonte_endpoint: Optional[str] = None
    payload_bruto: Optional[dict] = None
    confianca: float = 1.0
