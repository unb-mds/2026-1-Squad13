from typing import Protocol


class TokenBlacklistProvider(Protocol):
    """
    Interface para o provedor de blacklist de tokens.
    Define como o sistema deve interagir com o armazenamento de tokens revogados.
    """

    def adicionar_na_blacklist(self, token: str, expires_in_seconds: int) -> None:
        """
        Adiciona um token à blacklist com um tempo de expiração.
        """
        ...

    def esta_na_blacklist(self, token: str) -> bool:
        """
        Verifica se um token consta na blacklist.
        """
        ...
