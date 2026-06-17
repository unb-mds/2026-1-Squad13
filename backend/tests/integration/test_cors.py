from fastapi.testclient import TestClient

from main import app

client = TestClient(app, raise_server_exceptions=False)


def _cors_headers(origin: str) -> dict:
    return {
        "Origin": origin,
        "Access-Control-Request-Method": "GET",
    }


def test_cors_vercel_preview_url_aceita():
    """Origin de preview da Vercel com hash variável deve ser permitida pelo regex."""
    origin = "https://lextrack-frontend-abc123xyz-2026-1-squad13.vercel.app"
    response = client.options("/", headers=_cors_headers(origin))
    assert response.headers.get("access-control-allow-origin") == origin


def test_cors_vercel_preview_url_hash_diferente_aceita():
    """Qualquer hash diferente na URL de preview também deve ser aceito."""
    origin = "https://lextrack-frontend-8ykrpzm0v-2026-1-squad13.vercel.app"
    response = client.options("/", headers=_cors_headers(origin))
    assert response.headers.get("access-control-allow-origin") == origin


def test_cors_origin_nao_relacionada_bloqueada():
    """Origin de domínio externo não autorizado não deve receber header CORS."""
    origin = "https://evil.com"
    response = client.options("/", headers=_cors_headers(origin))
    assert response.headers.get("access-control-allow-origin") != origin


def test_cors_localhost_aceito():
    """Origin de localhost (padrão de dev) deve continuar funcionando via allow_origins."""
    origin = "http://localhost:5173"
    response = client.options("/", headers=_cors_headers(origin))
    assert response.headers.get("access-control-allow-origin") == origin
