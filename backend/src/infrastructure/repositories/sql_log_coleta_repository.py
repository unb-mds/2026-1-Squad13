from sqlmodel import Session

from application.ports.log_coleta_repository import LogColetaRepositoryPort
from infrastructure.database.models.log_coleta_model import LogColetaModel


class SQLLogColetaRepository(LogColetaRepositoryPort):
    """
    Implementação concreta do repositório de logs de coleta utilizando SQLModel.
    """

    def __init__(self, session: Session):
        self.session = session

    def salvar_log(
        self,
        fonte: str,
        status: str,
        itens_coletados: int,
        mensagem_erro: str | None = None,
    ) -> None:
        """
        Salva um registro de log da execução de coleta no banco de dados.
        """
        log = LogColetaModel(
            fonte=fonte,
            status=status,
            itens_coletados=itens_coletados,
            mensagem_erro=mensagem_erro,
        )
        self.session.add(log)
        self.session.commit()
