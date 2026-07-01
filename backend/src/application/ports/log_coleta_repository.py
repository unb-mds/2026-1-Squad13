from typing import Protocol


class LogColetaRepositoryPort(Protocol):
    """
    Interface (Port) para o repositório de log de coleta.
    Garante o desacoplamento do domínio/aplicação com a camada de infraestrutura.
    """

    def salvar_log(
        self,
        fonte: str,
        status: str,
        itens_coletados: int,
        mensagem_erro: str | None = None,
    ) -> None:
        """
        Salva um registro de log da execução de coleta.
        """
        ...
