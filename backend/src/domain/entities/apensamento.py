
from sqlmodel import SQLModel


class Apensamento(SQLModel):
    """
    Entidade de Domínio Pura para Apensamento.
    """

    apensamento_id: int | None = None
    materia_apensada_id: str
    materia_principal_id: str
    data_apensacao: str
    casa: str
    fonte_endpoint: str | None = None
    payload_bruto: dict | None = None
    confianca: float = 1.0
