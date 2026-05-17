from typing import Protocol, Optional


class PasswordResetTokenProvider(Protocol):
    def gerar_token(self, email: str) -> str:
        """Gera um token de uso único com TTL de 1 hora para o e-mail informado.
        Ao gerar um novo token, o anterior deve ser invalidado (ex: sobrescrevendo a chave no Redis)."""
        ...

    def validar_token(self, token: str) -> Optional[str]:
        """Valida o token e retorna o e-mail associado, ou None se inválido/expirado."""
        ...

    def invalidar_token(self, token: str) -> None:
        """Invalida o token (ex: após o uso) para garantir que seja de uso único."""
        ...
