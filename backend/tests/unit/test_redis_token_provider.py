from unittest.mock import MagicMock

import pytest
import redis

from infrastructure.cache.redis_token_provider import RedisPasswordResetTokenProvider


@pytest.fixture
def mock_redis():
    return MagicMock(spec=redis.Redis)


@pytest.fixture
def provider(mock_redis):
    return RedisPasswordResetTokenProvider(mock_redis)


def test_gerar_token_sucesso(provider, mock_redis):
    email = "test@example.com"
    mock_redis.get.return_value = None  # Nenhum token antigo

    token = provider.gerar_token(email)

    assert token is not None
    assert mock_redis.setex.call_count == 2
    # Verifica se salvou mapeamento token -> email e email -> token
    args_list = [call.args for call in mock_redis.setex.call_args_list]
    # Uma das chamadas deve ter o email como valor, a outra o token
    assert any(email in arg for arg in args_list)
    assert any(token in arg for arg in args_list)


def test_gerar_token_invalida_anterior(provider, mock_redis):
    email = "test@example.com"
    mock_redis.get.return_value = b"token_antigo"

    provider.gerar_token(email)

    mock_redis.delete.assert_called_once_with("pwd_reset_token:token_antigo")
    assert mock_redis.setex.call_count == 2


def test_validar_token_sucesso(provider, mock_redis):
    mock_redis.get.return_value = b"test@example.com"
    email = provider.validar_token("valid_token")
    assert email == "test@example.com"


def test_validar_token_inexistente(provider, mock_redis):
    mock_redis.get.return_value = None
    email = provider.validar_token("invalid_token")
    assert email is None


def test_invalidar_token_sucesso(provider, mock_redis):
    mock_redis.get.return_value = b"test@example.com"
    provider.invalidar_token("token_to_kill")
    assert mock_redis.delete.call_count == 2
    mock_redis.delete.assert_any_call("pwd_reset_token:token_to_kill")
    mock_redis.delete.assert_any_call("pwd_reset_email:test@example.com")


def test_gerar_token_redis_error(provider, mock_redis):
    mock_redis.get.side_effect = redis.RedisError("Erro")
    with pytest.raises(redis.RedisError):
        provider.gerar_token("test@example.com")


def test_validar_token_redis_error(provider, mock_redis):
    mock_redis.get.side_effect = redis.RedisError("Erro")
    assert provider.validar_token("token") is None


def test_invalidar_token_redis_error(provider, mock_redis):
    mock_redis.get.side_effect = redis.RedisError("Erro")
    # Não deve subir exceção, apenas logar
    provider.invalidar_token("token")
