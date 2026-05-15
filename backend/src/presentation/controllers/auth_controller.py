from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from infrastructure.database import get_session
from infrastructure.repositories.sql_user_repository import SQLUserRepository
from application.services.auth_service import AuthService
from domain.entities.user import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    repository = SQLUserRepository(session)
    return AuthService(repository)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_in: UserCreate, service: AuthService = Depends(get_auth_service)):
    """Registra um novo usuário."""
    return service.registrar_usuario(user_in)


@router.post("/login", response_model=Token)
def login(login_in: UserLogin, service: AuthService = Depends(get_auth_service)):
    """Autentica o usuário e retorna o token de acesso."""
    return service.login(login_in)
