from datetime import UTC, datetime

from sqlmodel import Session, select

from application.ports.auditoria_coleta_repository import AuditoriaColetaRepositoryPort
from infrastructure.database.models.auditoria_coleta_model import AuditoriaColetaModel


class SQLAuditoriaColetaRepository(AuditoriaColetaRepositoryPort):
    """
    Implementação concreta do repositório de auditoria de coleta utilizando SQLModel.
    """

    def __init__(self, session: Session):
        self.session = session

    def registrar_inicio(self, job_id: str, nome_job: str) -> None:
        """
        Registra o início de uma execução de background job.
        """
        statement = select(AuditoriaColetaModel).where(
            AuditoriaColetaModel.job_id == job_id
        )
        existing = self.session.exec(statement).first()
        if existing:
            return

        log = AuditoriaColetaModel(
            job_id=job_id,
            nome_job=nome_job,
            status="executando",
            data_inicio=datetime.now(UTC),
        )
        self.session.add(log)
        self.session.commit()

    def registrar_fim(
        self,
        job_id: str,
        status: str,
        itens_processados: int,
        mensagem_erro: str | None = None,
    ) -> None:
        """
        Registra a conclusão (sucesso ou falha) de um background job.
        """
        statement = select(AuditoriaColetaModel).where(
            AuditoriaColetaModel.job_id == job_id
        )
        log = self.session.exec(statement).first()
        if log:
            log.status = status
            log.data_fim = datetime.now(UTC)
            log.itens_processados = itens_processados
            log.mensagem_erro = mensagem_erro
            self.session.add(log)
            self.session.commit()

    def obter_ultima_execucao(
        self, nome_job: str | None = None
    ) -> AuditoriaColetaModel | None:
        """
        Recupera o registro da última execução (opcionalmente filtrando por nome).
        """
        statement = select(AuditoriaColetaModel)
        if nome_job:
            statement = statement.where(AuditoriaColetaModel.nome_job == nome_job)
        statement = statement.order_by(AuditoriaColetaModel.data_inicio.desc())
        return self.session.exec(statement).first()
