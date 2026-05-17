import os
import redis
from typing import Any, Optional
from application.ports.cache_provider import CacheProvider


class RedisClient(CacheProvider):
    """
    Implementação concreta do CacheProvider usando Redis.
    """

    def __init__(self, redis_url: str = None):
        if redis_url is None:
            # Default para a URL do Redis no docker-compose
            redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

        self.client = redis.Redis.from_url(redis_url, decode_responses=True)

    def get(self, key: str) -> Optional[Any]:
        """Recupera um valor do cache."""
        try:
            return self.client.get(key)
        except redis.RedisError as e:
            # Log de erro (idealmente usaria um logger)
            print(f"Erro ao aceder ao Redis (GET): {e}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Salva um valor no cache com um tempo de vida (TTL) opcional."""
        try:
            if ttl_seconds is not None:
                self.client.setex(key, ttl_seconds, value)
            else:
                self.client.set(key, value)
        except redis.RedisError as e:
            print(f"Erro ao aceder ao Redis (SET): {e}")

    def delete(self, key: str) -> None:
        """Remove um valor específico do cache."""
        try:
            self.client.delete(key)
        except redis.RedisError as e:
            print(f"Erro ao aceder ao Redis (DELETE): {e}")

    def invalidate(self, prefix: str) -> None:
        """Invalida todas as chaves que começam com o prefixo fornecido usando SCAN."""
        try:
            cursor = "0"
            while cursor != 0:
                cursor, keys = self.client.scan(
                    cursor=cursor, match=f"{prefix}*", count=100
                )
                if keys:
                    self.client.delete(*keys)
        except redis.RedisError as e:
            print(f"Erro ao aceder ao Redis (INVALIDATE): {e}")
