from datetime import datetime

from sqlmodel import SQLModel


class CoberturaSnapshot(SQLModel):
    """
    Entidade de Domínio Pura para snapshots de cobertura analítica.

    O campo `fonte` distingue snapshots por casa legislativa ("camara" | "senado"),
    evitando que a contagem de proposições das duas fontes seja somada e comparada
    com o total reportado por apenas uma delas (o que gerava cobertura fictícia > 100%).
    """

    id: int | None = None
    ano: int
    tipo_proposicao: str
    fonte: str = ""  # "camara" ou "senado" — vazio para snapshots legados
    total_api_oficial: int
    data_atualizacao: datetime
