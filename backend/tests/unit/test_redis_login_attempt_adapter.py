from unittest.mock import MagicMock

import pytest
import redis

from infrastructure.adapters.redis_login_attempt_adapter import RedisLoginAttemptAdapter


@pytest.fixture
def mock_redis():
    return MagicMock(spec=redis.Redis)


@pytest.fixture
def adapter(mock_redis):
    return RedisLoginAttemptAdapter(mock_redis)


def test_registrar_falha(adapter, mock_redis):
    mock_redis.incr.return_value = 1
    attempts = adapter.registrar_falha("user@example.com")
    assert attempts == 1
    mock_redis.expire.assert_called_once()


def test_esta_bloqueado_true(adapter, mock_redis):
    # Simula 5 tentativas (supondo max_attempts=5)
    mock_redis.get.return_value = b"5"
    adapter.max_attempts = 5
    assert adapter.esta_bloqueado("user@example.com") is True


def test_esta_bloqueado_false(adapter, mock_redis):
    mock_redis.get.return_value = b"2"
    adapter.max_attempts = 5
    assert adapter.esta_bloqueado("user@example.com") is False


def test_resetar_tentativas(adapter, mock_redis):
    adapter.resetar_tentativas("user@example.com")
    mock_redis.delete.assert_called_once_with("login_attempts:user@example.com")


def test_tempo_restante_bloqueio(adapter, mock_redis):
    mock_redis.ttl.return_value = 120
    assert adapter.tempo_restante_bloqueio("user@example.com") == 120


def test_redis_error_handling(adapter, mock_redis):
    mock_redis.incr.side_effect = redis.RedisError()
    assert adapter.registrar_falha("u") == 0

    mock_redis.get.side_effect = redis.RedisError()
    assert adapter.esta_bloqueado("u") is False

    mock_redis.delete.side_effect = redis.RedisError()
    adapter.resetar_tentativas("u")  # No exception

    mock_redis.ttl.side_effect = redis.RedisError()
    assert adapter.tempo_restante_bloqueio("u") == 0
