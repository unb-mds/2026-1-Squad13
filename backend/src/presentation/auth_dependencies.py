from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session
from infrastructure.database import get_session, get_redis_client
from infrastructure.repositories.sql_user_repository import SQLUserRepository
from infrastructure.adapters.security_adapter import decode_access_token
from infrastructure.adapters.redis_blacklist_adapter import RedisTokenBlacklistAdapter
from infrastructure.adapters.redis_login_attempt_adapter import RedisLoginAttemptAdapter
from infrastructure.adapters.dummy_email_sender import DummyEmailSender
from infrastructure.cache.redis_token_provider import RedisPasswordResetTokenProvider
from application.services.auth_service import AuthService
from application.services.recuperacao_senha_service import (
    SolicitarRecuperacaoSenhaUseCase,
    RedefinirSenhaUseCase,
)
from domain.exceptions import TokenRevogadoError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    """
    Injeção de dependência para o AuthService.
    Instancia o RedisTokenBlacklistAdapter, RedisLoginAttemptAdapter e o injeta.
    """
    repository = SQLUserRepository(session)
    redis_conn = get_redis_client()
    attempt_provider = RedisLoginAttemptAdapter(redis_conn)
    blacklist_adapter = RedisTokenBlacklistAdapter(redis_conn)
    return AuthService(
        repository, attempt_provider=attempt_provider, token_blacklist=blacklist_adapter
    )


def get_solicitar_recuperacao_usecase(
    session: Session = Depends(get_session),
) -> SolicitarRecuperacaoSenhaUseCase:
    user_repo = SQLUserRepository(session)
    redis_conn = get_redis_client()
    token_provider = RedisPasswordResetTokenProvider(redis_conn)
    email_sender = DummyEmailSender()
    return SolicitarRecuperacaoSenhaUseCase(user_repo, token_provider, email_sender)


def get_redefinir_senha_usecase(
    session: Session = Depends(get_session),
) -> RedefinirSenhaUseCase:
    user_repo = SQLUserRepository(session)
    redis_conn = get_redis_client()
    token_provider = RedisPasswordResetTokenProvider(redis_conn)
    return RedefinirSenhaUseCase(user_repo, token_provider)


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

    # 1. Verificar Blacklist PRIMEIRO
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
