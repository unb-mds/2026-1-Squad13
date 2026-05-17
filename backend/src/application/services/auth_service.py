import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from domain.entities.user import User, UserCreate, UserLogin, UserResponse, Token
from domain.exceptions import (
    TokenRevogadoError,
    ContaBloqueadaError,
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
)
from domain.services.login_attempt_service import LoginAttemptProvider
from application.ports.token_blacklist_provider import TokenBlacklistProvider
from infrastructure.repositories.sql_user_repository import SQLUserRepository
from infrastructure.adapters.security_adapter import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)
from infrastructure.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """
    Serviço de aplicação para gerenciar autenticação e usuários.
    """

    def __init__(
        self,
        user_repository: SQLUserRepository,
        attempt_provider: Optional[LoginAttemptProvider] = None,
        token_blacklist: Optional[TokenBlacklistProvider] = None,
    ):
        self.user_repository = user_repository
        self.attempt_provider = attempt_provider
        self.token_blacklist = token_blacklist

    def registrar_usuario(self, user_in: UserCreate) -> UserResponse:
        """Registra um novo usuário no sistema."""
        # Verifica se o usuário já existe
        if self.user_repository.buscar_por_email(user_in.email):
            raise EmailJaCadastradoError()

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
        # 1. Busca o usuário no banco primeiro para evitar spam no Redis com e-mails inexistentes
        user = self.user_repository.buscar_por_email(login_in.email)

        if not user:
            # Caso o usuário não exista, não tocamos no Redis para evitar poluição
            raise CredenciaisInvalidasError()

        # 2. Se o usuário existe, verifica se a conta está bloqueada
        if self.attempt_provider and self.attempt_provider.esta_bloqueado(
            login_in.email
        ):
            segundos = self.attempt_provider.tempo_restante_bloqueio(login_in.email)
            raise ContaBloqueadaError(login_in.email, segundos_restantes=segundos)

        # 3. Validação de senha
        if not verify_password(login_in.password, user.hashed_password):
            # Registra a falha apenas para usuários existentes
            if self.attempt_provider:
                self.attempt_provider.registrar_falha(login_in.email)

            raise CredenciaisInvalidasError()

        # 4. Login bem-sucedido: Reseta o contador de tentativas
        if self.attempt_provider:
            self.attempt_provider.resetar_tentativas(login_in.email)

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

    def logout(self, token: str) -> None:
        """
        Invalida o token JWT adicionando-o à blacklist.
        Calcula o TTL baseado no campo 'exp' do token.
        """
        if not self.token_blacklist:
            return

        try:
            payload = decode_access_token(token)
            exp = payload.get("exp")
            if exp:
                # exp é um timestamp Unix (segundos desde epoch)
                now = datetime.now(timezone.utc).timestamp()
                ttl = int(exp - now)

                if ttl > 0:
                    self.token_blacklist.adicionar_na_blacklist(token, ttl)
        except Exception as e:
            # Swallows exception to avoid breaking the logout response, but logs for monitoring
            logger.error(f"Falha ao processar logout/blacklist para o token: {e}")

    def verificar_token_blacklist(self, token: str) -> None:
        """
        Verifica se o token está na blacklist.
        Lança TokenRevogadoError se estiver.
        """
        if self.token_blacklist and self.token_blacklist.esta_na_blacklist(token):
            raise TokenRevogadoError("Token foi revogado")
