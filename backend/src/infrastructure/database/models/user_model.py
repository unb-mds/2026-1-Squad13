from typing import Optional

from sqlmodel import Field, SQLModel


class UserModel(SQLModel, table=True):
    """
    Modelo de persistência para Usuários.
    """

    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(index=True, unique=True)
    hashed_password: str
    perfil: str = "analista"
