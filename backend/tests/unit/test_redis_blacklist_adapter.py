from unittest.mock import MagicMock

import pytest
import redis

from infrastructure.adapters.redis_blacklist_adapter import RedisTokenBlacklistAdapter


@pytest.fixture
def mock_redis():
    return MagicMock(spec=redis.Redis)


@pytest.fixture
def adapter(mock_redis):
    return RedisTokenBlacklistAdapter(mock_redis)


def test_adicionar_na_blacklist(adapter, mock_redis):
    adapter.adicionar_na_blacklist("token123", 3600)
    mock_redis.setex.assert_called_once_with(
        name="blacklist:token:token123", time=3600, value="revogado"
    )


def test_esta_na_blacklist_true(adapter, mock_redis):
    mock_redis.exists.return_value = True
    assert adapter.esta_na_blacklist("token123") is True


def test_esta_na_blacklist_false(adapter, mock_redis):
    mock_redis.exists.return_value = False
    assert adapter.esta_na_blacklist("token123") is False


def test_redis_error_handling(adapter, mock_redis):
    mock_redis.setex.side_effect = redis.RedisError("Erro")
    # Deve apenas logar e não subir exceção (fail-open)
    adapter.adicionar_na_blacklist("token", 3600)

    mock_redis.exists.side_effect = redis.RedisError("Erro")
    assert adapter.esta_na_blacklist("token") is False
