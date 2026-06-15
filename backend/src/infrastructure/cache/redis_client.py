import logging
from typing import Any

import redis

from application.ports.cache_provider import CacheProvider

logger = logging.getLogger(__name__)


class RedisClient(CacheProvider):
    """
    Implementação concreta do CacheProvider usando Redis.
    """

    def __init__(self, redis_client: redis.Redis):
        self.client = redis_client
        self.cache_ttl = 86400  # 24 horas em segundos

    def get(self, key: str) -> Any | None:
        """Recupera um valor do cache."""
        try:
            return self.client.get(key)
        except redis.RedisError as e:
            logger.error(f"Erro ao acessar o Redis (GET): {e}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Salva um valor no cache com um tempo de vida (TTL) opcional."""
        try:
            if ttl_seconds is not None:
                self.client.setex(key, ttl_seconds, value)
            else:
                self.client.set(key, value)
        except redis.RedisError as e:
            logger.error(f"Erro ao acessar o Redis (SET): {e}")

    def delete(self, key: str) -> None:
        """Remove um valor específico do cache."""
        try:
            self.client.delete(key)
        except redis.RedisError as e:
            logger.error(f"Erro ao acessar o Redis (DELETE): {e}")

    def invalidate(self, prefix: str) -> None:
        """Invalida todas as chaves que começam com o prefixo fornecido usando SCAN."""
        try:
            cursor = 0
            while True:
                cursor, keys = self.client.scan(
                    cursor=cursor, match=f"{prefix}*", count=100
                )
                if keys:
                    self.client.delete(*keys)
                if cursor == 0:
                    break
        except redis.RedisError as e:
            logger.error(f"Erro ao acessar o Redis (INVALIDATE): {e}")
