from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(index=True, unique=True)
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
    email: Optional[str] = None
