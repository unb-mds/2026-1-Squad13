from typing import Protocol


class LoginAttemptProvider(Protocol):
    """
    Interface (Protocol) para gerenciamento de tentativas de login.
    Define o contrato para rastrear falhas e verificar bloqueios,
    permitindo que a aplicação não dependa de uma implementação específica (ex: Redis).
    """

    def registrar_falha(self, email: str) -> int:
        """Registra uma falha e retorna o número atual de tentativas."""
        ...

    def esta_bloqueado(self, email: str) -> bool:
        """Verifica se o e-mail informado está em período de bloqueio."""
        ...

    def resetar_tentativas(self, email: str) -> None:
        """Limpa o contador de tentativas após um login bem-sucedido."""
        ...
