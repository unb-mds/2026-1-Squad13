from application.ports.password_reset_token_provider import PasswordResetTokenProvider
from application.ports.email_sender_provider import EmailSenderProvider
from application.ports.user_repository import UserRepositoryPort
from domain.exceptions import UsuarioNaoEncontradoError, TokenInvalidoError
from infrastructure.adapters.security_adapter import get_password_hash


class SolicitarRecuperacaoSenhaUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        token_provider: PasswordResetTokenProvider,
        email_sender: EmailSenderProvider,
    ):
        self.user_repository = user_repository
        self.token_provider = token_provider
        self.email_sender = email_sender

    def executar(self, email: str) -> None:
        user = self.user_repository.buscar_por_email(email)
        if not user:
            raise UsuarioNaoEncontradoError("Usuário não encontrado.")

        token = self.token_provider.gerar_token(email)
        self.email_sender.enviar_email_recuperacao(email, token)


class RedefinirSenhaUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        token_provider: PasswordResetTokenProvider,
    ):
        self.user_repository = user_repository
        self.token_provider = token_provider

    def executar(self, token: str, nova_senha: str) -> None:
        email = self.token_provider.validar_token(token)
        if not email:
            raise TokenInvalidoError("Token inválido ou expirado.")

        user = self.user_repository.buscar_por_email(email)
        if not user:
            raise UsuarioNaoEncontradoError("Usuário não encontrado.")

        user.hashed_password = get_password_hash(nova_senha)
        self.user_repository.salvar(user)

        # Garante que o token seja de uso único
        self.token_provider.invalidar_token(token)
