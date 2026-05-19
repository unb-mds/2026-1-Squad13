import pytest
from unittest.mock import Mock

from application.services.recuperacao_senha_service import (
    SolicitarRecuperacaoSenhaUseCase,
    RedefinirSenhaUseCase,
)
from domain.exceptions import UsuarioNaoEncontradoError, TokenInvalidoError
from domain.entities.user import User


@pytest.fixture
def user_mock():
    return User(
        id=1,
        nome="Teste",
        email="teste@example.com",
        hashed_password="old_hashed_password",
        perfil="analista",
    )


@pytest.fixture
def repo_mock(user_mock):
    repo = Mock()
    repo.buscar_por_email.return_value = user_mock
    repo.salvar.return_value = user_mock
    return repo


@pytest.fixture
def token_provider_mock():
    provider = Mock()
    provider.gerar_token.return_value = "fake-token"
    provider.validar_token.return_value = "teste@example.com"
    return provider


@pytest.fixture
def email_sender_mock():
    return Mock()


def test_solicitar_recuperacao_senha_sucesso(
    repo_mock, token_provider_mock, email_sender_mock
):
    use_case = SolicitarRecuperacaoSenhaUseCase(
        repo_mock, token_provider_mock, email_sender_mock
    )

    use_case.executar("teste@example.com")

    repo_mock.buscar_por_email.assert_called_once_with("teste@example.com")
    token_provider_mock.gerar_token.assert_called_once_with("teste@example.com")
    email_sender_mock.enviar_email_recuperacao.assert_called_once_with(
        "teste@example.com", "fake-token"
    )


def test_solicitar_recuperacao_senha_usuario_nao_encontrado(
    repo_mock, token_provider_mock, email_sender_mock
):
    repo_mock.buscar_por_email.return_value = None
    use_case = SolicitarRecuperacaoSenhaUseCase(
        repo_mock, token_provider_mock, email_sender_mock
    )

    with pytest.raises(UsuarioNaoEncontradoError):
        use_case.executar("invalido@example.com")

    token_provider_mock.gerar_token.assert_not_called()
    email_sender_mock.enviar_email_recuperacao.assert_not_called()


def test_redefinir_senha_sucesso(repo_mock, token_provider_mock):
    use_case = RedefinirSenhaUseCase(repo_mock, token_provider_mock)

    use_case.executar("fake-token", "nova_senha_123")

    token_provider_mock.validar_token.assert_called_once_with("fake-token")
    repo_mock.buscar_por_email.assert_called_once_with("teste@example.com")
    repo_mock.salvar.assert_called_once()
    token_provider_mock.invalidar_token.assert_called_once_with("fake-token")

    # Verifica se a senha foi hasheada e atualizada
    user_salvo = repo_mock.salvar.call_args[0][0]
    assert user_salvo.hashed_password != "old_hashed_password"


def test_redefinir_senha_token_invalido(repo_mock, token_provider_mock):
    token_provider_mock.validar_token.return_value = None
    use_case = RedefinirSenhaUseCase(repo_mock, token_provider_mock)

    with pytest.raises(TokenInvalidoError):
        use_case.executar("invalid-token", "nova_senha_123")

    repo_mock.salvar.assert_not_called()
    token_provider_mock.invalidar_token.assert_not_called()


def test_redefinir_senha_usuario_nao_encontrado(repo_mock, token_provider_mock):
    repo_mock.buscar_por_email.return_value = None
    use_case = RedefinirSenhaUseCase(repo_mock, token_provider_mock)

    with pytest.raises(UsuarioNaoEncontradoError):
        use_case.executar("fake-token", "nova_senha_123")

    repo_mock.salvar.assert_not_called()
    token_provider_mock.invalidar_token.assert_not_called()


def test_solicitar_recuperacao_invalida_token_anterior_em_memoria():
    """
    Testa a lógica usando um mock de provider em memória para demonstrar o comportamento
    de invalidação/substituição do token (que ocorrerá nativamente no Redis ao sobrescrever a chave).
    """

    class InMemoryTokenProvider:
        def __init__(self):
            self.store = {}

        def gerar_token(self, email: str) -> str:
            import uuid

            token = str(uuid.uuid4())
            # Limpa tokens anteriores do mesmo e-mail
            tokens_antigos = [k for k, v in self.store.items() if v == email]
            for t in tokens_antigos:
                del self.store[t]
            self.store[token] = email
            return token

        def validar_token(self, token: str) -> str:
            return self.store.get(token)

        def invalidar_token(self, token: str) -> None:
            if token in self.store:
                del self.store[token]

    provider = InMemoryTokenProvider()
    repo = Mock()
    repo.buscar_por_email.return_value = User(
        id=1, nome="T", email="a@a.com", hashed_password="h", perfil="analista"
    )
    sender = Mock()

    use_case_solicitar = SolicitarRecuperacaoSenhaUseCase(repo, provider, sender)

    # Primeira solicitação
    use_case_solicitar.executar("a@a.com")
    token1 = sender.enviar_email_recuperacao.call_args_list[0][0][1]

    # Segunda solicitação (deve invalidar o token1)
    use_case_solicitar.executar("a@a.com")
    token2 = sender.enviar_email_recuperacao.call_args_list[1][0][1]

    assert provider.validar_token(token1) is None
    assert provider.validar_token(token2) == "a@a.com"


def test_redefinir_senha_segunda_utilizacao_falha():
    class InMemoryTokenProvider:
        def __init__(self):
            self.store = {"token-valido": "a@a.com"}

        def validar_token(self, token: str) -> str:
            return self.store.get(token)

        def invalidar_token(self, token: str) -> None:
            if token in self.store:
                del self.store[token]

    provider = InMemoryTokenProvider()
    repo = Mock()
    repo.buscar_por_email.return_value = User(
        id=1, nome="T", email="a@a.com", hashed_password="h", perfil="analista"
    )

    use_case = RedefinirSenhaUseCase(repo, provider)

    # Primeira utilização: sucesso
    use_case.executar("token-valido", "nova")
    assert provider.validar_token("token-valido") is None

    # Segunda utilização: falha
    with pytest.raises(TokenInvalidoError):
        use_case.executar("token-valido", "outra")
