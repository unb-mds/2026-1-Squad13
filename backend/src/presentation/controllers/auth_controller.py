from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from infrastructure.database import get_session
from infrastructure.repositories.sql_user_repository import SQLUserRepository
from infrastructure.adapters.redis_login_attempt_adapter import RedisLoginAttemptAdapter
from application.services.auth_service import AuthService
from domain.entities.user import UserCreate, UserLogin, UserResponse, Token
from domain.exceptions import ContaBloqueadaError

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    repository = SQLUserRepository(session)
    attempt_provider = RedisLoginAttemptAdapter()
    return AuthService(repository, attempt_provider)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_in: UserCreate, service: AuthService = Depends(get_auth_service)):
    """Registra um novo usuário."""
    return service.registrar_usuario(user_in)


@router.post("/login", response_model=Token)
def login(login_in: UserLogin, service: AuthService = Depends(get_auth_service)):
    """Autentica o usuário e retorna o token de acesso."""
    try:
        return service.login(login_in)
    except ContaBloqueadaError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
        )
