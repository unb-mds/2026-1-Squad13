from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class AuditoriaColetaModel(SQLModel, table=True):
    """
    Representa o registro de auditoria para execuções de tarefas de coleta (background jobs).
    """

    __tablename__ = "auditoria_coleta"

    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(
        index=True,
        unique=True,
        description="Identificador único da execução (ex: task_id do Celery)",
    )
    nome_job: str = Field(description="Nome ou tipo do job executado")
    status: str = Field(
        description="Status da execução do job (ex: 'executando', 'sucesso', 'falha')"
    )
    data_inicio: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Data e hora do início da execução",
    )
    data_fim: datetime | None = Field(
        default=None, nullable=True, description="Data e hora do fim da execução"
    )
    itens_processados: int = Field(
        default=0, description="Total de itens coletados/atualizados"
    )
    mensagem_erro: str | None = Field(
        default=None,
        nullable=True,
        description="Traceback ou mensagem em caso de falha",
    )
