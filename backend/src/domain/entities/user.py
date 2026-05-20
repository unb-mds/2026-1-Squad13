from sqlmodel import SQLModel


class User(SQLModel):
    """
    Entidade de Domínio Pura para Usuário.
    """

    id: int | None = None
    nome: str
    email: str
    hashed_password: str
    perfil: str = "analista"


class UserCreate(SQLModel):
    nome: str
    email: str
    password: str


class UserLogin(SQLModel):
    email: str
    password: str


class UserResponse(SQLModel):
    id: int
    nome: str
    email: str
    perfil: str


class Token(SQLModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(SQLModel):
    email: str | None = None
