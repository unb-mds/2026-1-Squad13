from typing import Protocol

from domain.entities.user import User


class UserRepositoryPort(Protocol):
    def buscar_por_email(self, email: str) -> User | None: ...

    def salvar(self, user: User) -> User: ...
