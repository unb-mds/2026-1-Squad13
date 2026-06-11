from typing import Any, Protocol


class AuditoriaColetaRepositoryPort(Protocol):
    """
    Interface (Port) para o repositório de auditoria de coleta.
    Garante o desacoplamento entre a aplicação e a infraestrutura.
    """

    def registrar_inicio(self, job_id: str, nome_job: str) -> None:
        """
        Registra o início de uma execução de background job.
        """
        ...

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
        ...

    def obter_ultima_execucao(self, nome_job: str | None = None) -> Any:
        """
        Recupera o registro da última execução (opcionalmente filtrando por nome).
        """
        ...
