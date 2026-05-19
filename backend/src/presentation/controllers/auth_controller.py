import logging
from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException
from pydantic import BaseModel
from presentation.auth_dependencies import (
    get_auth_service,
    get_solicitar_recuperacao_usecase,
    get_redefinir_senha_usecase,
    oauth2_scheme,
)
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

router = APIRouter(prefix="/auth", tags=["Autenticação"])

logger = logging.getLogger(__name__)


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


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    token: str = Depends(oauth2_scheme),
    service: AuthService = Depends(get_auth_service),
):
    """
    Realiza o logout do usuário, invalidando o token JWT atual na blacklist.
    """
    service.logout(token)
    return {"message": "Logout realizado com sucesso"}


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

    def background_task():
        try:
            usecase.executar(request.email)
        except UsuarioNaoEncontradoError:
            logger.warning(
                f"Tentativa de recuperação de senha para e-mail não cadastrado: {request.email}"
            )

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
