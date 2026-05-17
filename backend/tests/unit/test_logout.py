import pytest
from datetime import datetime, timezone, timedelta
from jose import jwt
from application.services.auth_service import AuthService
from infrastructure.config import settings
from domain.exceptions import TokenRevogadoError


class MockTokenBlacklistProvider:
    def __init__(self):
        self.blacklist = set()

    def adicionar_na_blacklist(self, token: str, expires_in_seconds: int) -> None:
        self.blacklist.add(token)

    def esta_na_blacklist(self, token: str) -> bool:
        return token in self.blacklist


@pytest.fixture
def mock_blacklist():
    return MockTokenBlacklistProvider()


@pytest.fixture
def auth_service(mock_blacklist):
    # Passamos None para o repositório pois não vamos usá-lo nestes testes
    return AuthService(user_repository=None, token_blacklist=mock_blacklist)


def test_logout_adiciona_token_na_blacklist(auth_service, mock_blacklist):
    # 1. Gerar um token válido
    exp = datetime.now(timezone.utc) + timedelta(minutes=15)
    token = jwt.encode(
        {"sub": "user@test.com", "exp": exp},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    # 2. Executar logout
    auth_service.logout(token)

    # 3. Verificar se está na blacklist
    assert mock_blacklist.esta_na_blacklist(token) is True


def test_verificar_token_blacklist_lanca_excecao(auth_service, mock_blacklist):
    token = "token-revogado"
    mock_blacklist.adicionar_na_blacklist(token, 3600)

    with pytest.raises(TokenRevogadoError) as excinfo:
        auth_service.verificar_token_blacklist(token)
    
    assert "Token foi revogado" in str(excinfo.value)


def test_logout_calcula_ttl_corretamente(auth_service, mock_blacklist, monkeypatch):
    # Fixar o tempo atual (usando um ano no futuro para garantir que não expire)
    now_fixed = datetime(2030, 5, 17, 12, 0, 0, tzinfo=timezone.utc)

    # Mock datetime.now dentro do módulo do serviço
    class MockDatetime:
        @classmethod
        def now(cls, tz=None):
            return now_fixed

    import application.services.auth_service
    monkeypatch.setattr(application.services.auth_service, "datetime", MockDatetime)

    # Criar token que expira em 10 minutos (600 segundos à frente do tempo fixado)
    exp_time = now_fixed + timedelta(minutes=10)
    token = jwt.encode(
        {"sub": "user@test.com", "exp": exp_time},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    captured_ttl = []
    def mock_adicionar(token_str, ttl):
        captured_ttl.append(ttl)

    monkeypatch.setattr(mock_blacklist, "adicionar_na_blacklist", mock_adicionar)

    auth_service.logout(token)

    # O TTL deve ser exatamente 600 segundos
    assert len(captured_ttl) > 0
    assert captured_ttl[0] == 600
