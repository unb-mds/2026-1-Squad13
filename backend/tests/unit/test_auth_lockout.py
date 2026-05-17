import pytest
from unittest.mock import MagicMock
from application.services.auth_service import AuthService
from domain.entities.user import User, UserLogin
from domain.exceptions import ContaBloqueadaError, CredenciaisInvalidasError


class MockLoginAttemptProvider:
    def __init__(self):
        self.attempts = {}
        self.blocked = set()

    def registrar_falha(self, email: str) -> int:
        count = self.attempts.get(email, 0) + 1
        self.attempts[email] = count
        if count >= 5:
            self.blocked.add(email)
        return count

    def esta_bloqueado(self, email: str) -> bool:
        return email in self.blocked

    def resetar_tentativas(self, email: str) -> None:
        if email in self.attempts:
            del self.attempts[email]
        if email in self.blocked:
            self.blocked.remove(email)


@pytest.fixture
def user_repository():
    return MagicMock()


@pytest.fixture
def attempt_provider():
    return MockLoginAttemptProvider()


@pytest.fixture
def auth_service(user_repository, attempt_provider):
    return AuthService(user_repository, attempt_provider)


def test_login_sucesso_reseta_tentativas(
    auth_service, user_repository, attempt_provider
):
    # Setup
    email = "test@example.com"
    password = "password123"
    hashed_password = "hashed_password"
    user = User(
        id=1,
        nome="Test",
        email=email,
        hashed_password=hashed_password,
        perfil="analista",
    )

    user_repository.buscar_por_email.return_value = user

    # Mock verify_password to return True
    with MagicMock():
        import application.services.auth_service as auth_mod

        auth_mod.verify_password = MagicMock(return_value=True)
        auth_mod.create_access_token = MagicMock(return_value="fake-token")

        # Simula algumas falhas prévias
        attempt_provider.registrar_falha(email)
        assert attempt_provider.attempts[email] == 1

        # Ação
        auth_service.login(UserLogin(email=email, password=password))

        # Verificação
        assert email not in attempt_provider.attempts
        assert not attempt_provider.esta_bloqueado(email)


def test_login_falha_email_inexistente_nao_deve_tocar_no_redis(
    auth_service, user_repository, attempt_provider
):
    # Setup
    email = "inexistente@example.com"
    user_repository.buscar_por_email.return_value = None  # Usuário não encontrado

    # Ação & Verificação
    with pytest.raises(CredenciaisInvalidasError):
        auth_service.login(UserLogin(email=email, password="any"))

    # Não deve haver registro no mock de tentativas
    assert email not in attempt_provider.attempts


def test_login_falha_senha_errada_deve_incrementar_tentativas(
    auth_service, user_repository, attempt_provider
):
    # Setup
    email = "test@example.com"
    user = User(
        id=1, nome="Test", email=email, hashed_password="hashed", perfil="analista"
    )
    user_repository.buscar_por_email.return_value = user

    with MagicMock():
        import application.services.auth_service as auth_mod
        auth_mod.verify_password = MagicMock(return_value=False)

        # Ação & Verificação
        with pytest.raises(CredenciaisInvalidasError):
            auth_service.login(UserLogin(email=email, password="wrong"))

        assert attempt_provider.attempts[email] == 1


def test_bloqueio_apos_cinco_falhas_usuario_existente(
    auth_service, user_repository, attempt_provider
):
    # Setup
    email = "test@example.com"
    user = User(
        id=1, nome="Test", email=email, hashed_password="hashed", perfil="analista"
    )
    user_repository.buscar_por_email.return_value = user

    with MagicMock():
        import application.services.auth_service as auth_mod
        auth_mod.verify_password = MagicMock(return_value=False)

        # Simula 5 falhas
        for _ in range(5):
            with pytest.raises(CredenciaisInvalidasError):
                auth_service.login(UserLogin(email=email, password="wrong"))

        assert attempt_provider.attempts[email] == 5
        assert attempt_provider.esta_bloqueado(email)

        # 6ª tentativa: Deve lançar ContaBloqueadaError
        with pytest.raises(ContaBloqueadaError):
            auth_service.login(UserLogin(email=email, password="any"))
