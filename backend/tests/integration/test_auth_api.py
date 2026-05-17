from fastapi.testclient import TestClient
from domain.entities.user import User
from infrastructure.adapters.security_adapter import get_password_hash


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
        perfil="analista"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

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
        perfil="analista"
    )
    db_session.add(user)
    db_session.commit()

    login_data = {
        "email": email_teste,
        "password": "senhaerrada",
    }
    response = http_client.post("/auth/login", json=login_data)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha incorretos"
