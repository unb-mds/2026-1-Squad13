from unittest.mock import patch

from fastapi.testclient import TestClient

from domain.entities.user import User
from infrastructure.adapters.security_adapter import get_password_hash
from infrastructure.repositories.sql_user_repository import SQLUserRepository


def test_login_caminho_feliz(http_client: TestClient, db_session):
    """
    Testa o cenário 'Caminho Feliz' do login.
    Insere um usuário no banco e faz login para obter o access_token.
    """
    # 1. Inserir um usuário no banco de dados em memória
    email_teste = "demo@lextrack.gov.br"
    senha_teste = "demo123"

    user = User(
        nome="Usuário Demo",
        email=email_teste,
        hashed_password=get_password_hash(senha_teste),
        perfil="analista",
    )
    repo = SQLUserRepository(db_session)
    repo.salvar(user)

    # 2. Tentar fazer login com as credenciais corretas
    login_data = {
        "email": email_teste,
        "password": senha_teste,
    }
    response = http_client.post("/auth/login", json=login_data)

    # 3. Asserts
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["user"]["email"] == email_teste


def test_login_falha_tratada_email_nao_existe(http_client: TestClient):
    """
    Testa o cenário 'Falha Tratada' com um e-mail que não existe no banco.
    Deve retornar 401 Unauthorized e não 500 Internal Server Error.
    """
    login_data = {
        "email": "inexistente@lextrack.gov.br",
        "password": "qualquersenha",
    }
    response = http_client.post("/auth/login", json=login_data)

    # Valida que o erro foi tratado como 401 e não 500
    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha incorretos"


def test_login_falha_tratada_senha_incorreta(http_client: TestClient, db_session):
    """
    Testa o cenário 'Falha Tratada' com senha incorreta.
    Deve retornar 401 Unauthorized.
    """
    email_teste = "demo2@lextrack.gov.br"
    senha_correta = "demo123"

    user = User(
        nome="Usuário Demo 2",
        email=email_teste,
        hashed_password=get_password_hash(senha_correta),
        perfil="analista",
    )
    repo = SQLUserRepository(db_session)
    repo.salvar(user)

    login_data = {
        "email": email_teste,
        "password": "senhaerrada",
    }
    response = http_client.post("/auth/login", json=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha incorretos"


def test_logout_sucesso(http_client: TestClient, db_session):
    email = "logout@test.com"
    user = User(
        id=999, nome="Logout", email=email, hashed_password="X", perfil="analista"
    )
    repo = SQLUserRepository(db_session)
    repo.salvar(user)

    # Login para obter token
    login_data = {"email": email, "password": "X"}
    # Mock do auth_service para permitir login com senha fake
    with patch("application.services.auth_service.AuthService.login") as mock_login:
        from domain.entities.user import Token

        mock_login.return_value = Token(
            access_token="fake_token", token_type="bearer", user=user
        )
        login_resp = http_client.post("/auth/login", json=login_data)
        token = login_resp.json()["access_token"]

        # Act: Logout
        headers = {"Authorization": f"Bearer {token}"}
        resp = http_client.post("/auth/logout", headers=headers)

        assert resp.status_code == 200
        assert resp.json() == {"message": "Logout realizado com sucesso"}


def test_solicitar_recuperacao_sucesso(http_client: TestClient, db_session):
    email = "recover@test.com"
    user = User(nome="R", email=email, hashed_password="X", perfil="analista")
    repo = SQLUserRepository(db_session)
    repo.salvar(user)

    resp = http_client.post("/auth/recuperar-senha", json={"email": email})
    assert resp.status_code == 202
    assert "message" in resp.json()
