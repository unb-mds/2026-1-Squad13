from fastapi import APIRouter, Depends, status, HTTPException
from presentation.auth_dependencies import get_auth_service, oauth2_scheme
from application.services.auth_service import AuthService
from domain.entities.user import UserCreate, UserLogin, UserResponse, Token
from domain.exceptions import UsuarioJaCadastradoError, CredenciaisInvalidasError

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_in: UserCreate, service: AuthService = Depends(get_auth_service)):
    """Registra um novo usuário."""
    try:
        return service.registrar_usuario(user_in)
    except UsuarioJaCadastradoError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
def login(login_in: UserLogin, service: AuthService = Depends(get_auth_service)):
    """Autentica o usuário e retorna o token de acesso."""
    try:
        return service.login(login_in)
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
