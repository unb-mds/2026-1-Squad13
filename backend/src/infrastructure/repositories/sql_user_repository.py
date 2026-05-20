from sqlmodel import Session, select

from domain.entities.user import User
from infrastructure.database.models.user_model import UserModel


class SQLUserRepository:
    """
    Implementação do repositório de usuários utilizando SQLModel e PostgreSQL.
    Opera sobre UserModel (infra) e retorna User (domínio).
    """

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: UserModel) -> User:
        return User.model_validate(model.model_dump())

    def _to_model(self, entity: User) -> UserModel:
        return UserModel.model_validate(entity.model_dump())

    def salvar(self, user: User) -> User:
        """Salva ou atualiza um usuário no banco."""
        model = self._to_model(user)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def buscar_por_email(self, email: str) -> User | None:
        """Busca um usuário pelo e-mail."""
        statement = select(UserModel).where(UserModel.email == email)
        model = self.session.exec(statement).first()
        return self._to_entity(model) if model else None

    def buscar_por_id(self, user_id: int) -> User | None:
        """Busca um usuário pelo ID."""
        model = self.session.get(UserModel, user_id)
        return self._to_entity(model) if model else None
