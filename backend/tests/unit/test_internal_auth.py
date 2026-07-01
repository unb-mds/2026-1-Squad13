import pytest
from fastapi import HTTPException

from infrastructure.config import settings
from presentation.internal_auth import verify_internal_token


@pytest.mark.asyncio
async def test_verify_internal_token_success(monkeypatch):
    monkeypatch.setattr(settings, "INTERNAL_API_SECRET", "super-secret")
    # Deve executar com sucesso sem lançar exceção
    await verify_internal_token("super-secret")


@pytest.mark.asyncio
async def test_verify_internal_token_missing_secret(monkeypatch):
    monkeypatch.setattr(settings, "INTERNAL_API_SECRET", "")
    with pytest.raises(HTTPException) as exc_info:
        await verify_internal_token("any-token")
    assert exc_info.value.status_code == 503
    assert "não configurado" in exc_info.value.detail


@pytest.mark.asyncio
async def test_verify_internal_token_invalid(monkeypatch):
    monkeypatch.setattr(settings, "INTERNAL_API_SECRET", "super-secret")
    with pytest.raises(HTTPException) as exc_info:
        await verify_internal_token("wrong-token")
    assert exc_info.value.status_code == 401
    assert "Token inválido" in exc_info.value.detail
