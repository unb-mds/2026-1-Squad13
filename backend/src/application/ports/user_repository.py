from typing import Optional, Protocol

from domain.entities.user import User


class UserRepositoryPort(Protocol):
    def buscar_por_email(self, email: str) -> Optional[User]: ...

    def salvar(self, user: User) -> User: ...
