from datetime import timedelta
from fastapi import HTTPException, status
from domain.entities.user import User, UserCreate, UserLogin, UserResponse, Token
from infrastructure.repositories.sql_user_repository import SQLUserRepository
from infrastructure.adapters.security_adapter import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from infrastructure.config import settings


class AuthService:
    """
    Serviço de aplicação para gerenciar autenticação e usuários.
    """

    def __init__(self, user_repository: SQLUserRepository):
        self.user_repository = user_repository

    def registrar_usuario(self, user_in: UserCreate) -> UserResponse:
        """Registra um novo usuário no sistema."""
        # Verifica se o usuário já existe
        if self.user_repository.buscar_por_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado"
            )

        # Cria a entidade de usuário com a senha hasheada
        user = User(
            nome=user_in.nome,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            perfil="analista",  # Perfil padrão conforme requisitos
        )

        user_salvo = self.user_repository.salvar(user)

        return UserResponse(
            id=user_salvo.id,
            nome=user_salvo.nome,
            email=user_salvo.email,
            perfil=user_salvo.perfil,
        )

    def login(self, login_in: UserLogin) -> Token:
        """Autentica um usuário e retorna um token JWT."""
        user = self.user_repository.buscar_por_email(login_in.email)

        if not user or not verify_password(login_in.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Gera o token de acesso
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id, nome=user.nome, email=user.email, perfil=user.perfil
            ),
        )
