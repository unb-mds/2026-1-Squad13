from fastapi.testclient import TestClient

def test_register_and_login_flow(http_client: TestClient):
    # 1. Registrar um novo usuário
    register_data = {
        "nome": "Usuário Teste",
        "email": "teste@exemplo.com",
        "password": "senha_segura_123"
    }
    response = http_client.post("/auth/register", json=register_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == register_data["email"]
    assert data["nome"] == register_data["nome"]
    assert "id" in data

    # 2. Tentar registrar com o mesmo e-mail (deve falhar)
    response = http_client.post("/auth/register", json=register_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "E-mail já cadastrado"

    # 3. Fazer login
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    response = http_client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["user"]["email"] == register_data["email"]

    # 4. Fazer login com senha errada
    login_data["password"] = "senha_errada"
    response = http_client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha incorretos"
