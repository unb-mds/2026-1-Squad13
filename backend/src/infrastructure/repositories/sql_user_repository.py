from typing import Optional
from sqlmodel import Session, select
from domain.entities.user import User

class SQLUserRepository:
    """
    Implementação do repositório de usuários utilizando SQLModel e PostgreSQL.
    """
    def __init__(self, session: Session):
        self.session = session

    def salvar(self, user: User) -> User:
        """Salva ou atualiza um usuário no banco."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def buscar_por_email(self, email: str) -> Optional[User]:
        """Busca um usuário pelo e-mail."""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def buscar_por_id(self, user_id: int) -> Optional[User]:
        """Busca um usuário pelo ID."""
        return self.session.get(User, user_id)
