from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class LogColetaModel(SQLModel, table=True):
    """
    Representa o log de execução de uma tarefa de coleta em lote (batch).
    """

    __tablename__ = "log_coleta_batch"

    id: int | None = Field(default=None, primary_key=True)
    data_hora: datetime = Field(default_factory=lambda: datetime.now(UTC))
    fonte: str = Field(index=True, description="Ex: 'camara' ou 'senado'")
    status: str = Field(description="Ex: 'sucesso' ou 'falha'")
    itens_coletados: int = Field(default=0)
    mensagem_erro: str | None = None
