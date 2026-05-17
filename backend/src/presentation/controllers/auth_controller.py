from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException
from sqlmodel import Session
from pydantic import BaseModel
import redis
from infrastructure.database import get_session
from infrastructure.repositories.sql_user_repository import SQLUserRepository
from infrastructure.adapters.redis_login_attempt_adapter import RedisLoginAttemptAdapter
from application.services.auth_service import AuthService
from application.services.recuperacao_senha_service import (
    SolicitarRecuperacaoSenhaUseCase,
    RedefinirSenhaUseCase,
)
from domain.entities.user import UserCreate, UserLogin, UserResponse, Token
from domain.exceptions import (
    UsuarioNaoEncontradoError,
    TokenInvalidoError,
    ContaBloqueadaError,
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
)
from infrastructure.cache.redis_token_provider import RedisPasswordResetTokenProvider
from infrastructure.adapters.dummy_email_sender import DummyEmailSender
from infrastructure.config import settings

router = APIRouter(prefix="/auth", tags=["Autenticação"])


# Dependência do Redis (poderia vir de um get_redis_client no config, mas usaremos uma instância simples aqui para dev)
def get_redis_client():
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    repository = SQLUserRepository(session)
    attempt_provider = RedisLoginAttemptAdapter()
    return AuthService(repository, attempt_provider)


def get_solicitar_recuperacao_usecase(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis_client),
) -> SolicitarRecuperacaoSenhaUseCase:
    user_repo = SQLUserRepository(session)
    token_provider = RedisPasswordResetTokenProvider(redis_client)
    email_sender = DummyEmailSender()
    return SolicitarRecuperacaoSenhaUseCase(user_repo, token_provider, email_sender)


def get_redefinir_senha_usecase(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis_client),
) -> RedefinirSenhaUseCase:
    user_repo = SQLUserRepository(session)
    token_provider = RedisPasswordResetTokenProvider(redis_client)
    return RedefinirSenhaUseCase(user_repo, token_provider)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_in: UserCreate, service: AuthService = Depends(get_auth_service)):
    """Registra um novo usuário."""
    try:
        return service.registrar_usuario(user_in)
    except EmailJaCadastradoError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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
    except CredenciaisInvalidasError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


class RecuperacaoSenhaRequest(BaseModel):
    email: str


class RedefinirSenhaRequest(BaseModel):
    token: str
    nova_senha: str


@router.post("/recuperar-senha", status_code=status.HTTP_202_ACCEPTED)
def solicitar_recuperacao_senha(
    request: RecuperacaoSenhaRequest,
    background_tasks: BackgroundTasks,
    usecase: SolicitarRecuperacaoSenhaUseCase = Depends(
        get_solicitar_recuperacao_usecase
    ),
):
    """Solicita a recuperação de senha e envia o link por e-mail (processado em background)."""
    # A execução do caso de uso pode levantar UsuarioNaoEncontradoError,
    # porém, por segurança, muitas vezes é recomendado retornar 202 mesmo se o usuário não existir
    # para evitar vazamento de e-mails cadastrados (User Enumeration).
    # Como não especificado e é boa prática, manteremos assim e engoliremos o erro de domínio no background
    # MAS como o requisito é apenas background tasks:

    def background_task():
        try:
            usecase.executar(request.email)
        except UsuarioNaoEncontradoError:
            pass  # Ignora para não vazar info, ou loga a tentativa

    background_tasks.add_task(background_task)
    return {
        "message": "Se o e-mail estiver cadastrado, você receberá um link de recuperação em breve."
    }


@router.post("/redefinir-senha", status_code=status.HTTP_200_OK)
def redefinir_senha(
    request: RedefinirSenhaRequest,
    usecase: RedefinirSenhaUseCase = Depends(get_redefinir_senha_usecase),
):
    """Redefine a senha utilizando o token recebido por e-mail."""
    try:
        usecase.executar(request.token, request.nova_senha)
        return {"message": "Senha redefinida com sucesso."}
    except TokenInvalidoError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UsuarioNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
