from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session
from infrastructure.database import get_session
from infrastructure.repositories.sql_user_repository import SQLUserRepository
from infrastructure.adapters.security_adapter import decode_access_token
from application.services.auth_service import AuthService
from domain.exceptions import TokenRevogadoError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    """
    Injeção de dependência para o AuthService.
    Por enquanto, o token_blacklist é None até implementarmos o adaptador Redis.
    """
    repository = SQLUserRepository(session)
    # Aqui poderíamos injetar o provedor real no futuro
    return AuthService(repository, token_blacklist=None)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Dependência central para validar o JWT e verificar a blacklist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Verificar Blacklist PRIMEIRO (conforme GEMINI.md)
    try:
        auth_service.verificar_token_blacklist(token)
    except TokenRevogadoError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revogado. Faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Decodificar e validar JWT
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = auth_service.user_repository.buscar_por_email(email)
    if user is None:
        raise credentials_exception

    return user
