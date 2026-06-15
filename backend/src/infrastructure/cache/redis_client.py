import logging
from collections.abc import Callable
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

    def set_nx(self, key: str, value: Any, ttl_seconds: int) -> bool:
        """Salva no cache apenas se a chave não existir. Retorna True se criada."""
        try:
            # nx=True e ex=ttl_seconds é equivalente ao comando SET key value NX EX ttl
            return bool(self.client.set(key, value, nx=True, ex=ttl_seconds))
        except redis.RedisError as e:
            logger.error(f"Erro ao acessar o Redis (SETNX): {e}")
            return False

    def eval_lua(self, script: str, keys: list[str], args: list[Any]) -> Any:
        """Executa um script Lua atômico no provedor de cache."""
        try:
            return self.client.eval(script, len(keys), *keys, *args)
        except redis.RedisError as e:
            logger.error(f"Erro ao acessar o Redis (EVAL LUA): {e}")
            raise

    def obter_e_atualizar_multichaves_seguro(
        self, keys: list[str], update_fn: Callable[[list[Any]], dict[str, Any] | None]
    ) -> bool:
        """Executa uma atualização transacional segura (Optimistic Locking) em múltiplas chaves."""
        import random
        import time

        max_retries = 3

        for attempt in range(max_retries):
            with self.client.pipeline() as pipe:
                try:
                    pipe.watch(*keys)
                    # Lemos os valores atuais no pipeline
                    values_raw = [pipe.get(k) for k in keys]
                    # Decodificamos bytes para string se necessário
                    values = [
                        v.decode() if isinstance(v, bytes) else v for v in values_raw
                    ]
                    # A função callback calcula os novos valores
                    novos_valores = update_fn(values)
                    if novos_valores is None:
                        pipe.unwatch()
                        return False

                    pipe.multi()
                    for k, v in novos_valores.items():
                        pipe.set(k, str(v))
                    pipe.execute()
                    return True
                except redis.WatchError:
                    if attempt < max_retries - 1:
                        jitter = random.uniform(0.01, 0.05)
                        time.sleep(jitter)
                    else:
                        logger.error(
                            f"Falha persistente (WatchError) ao atualizar chaves {keys} após {max_retries} tentativas."
                        )
                        return False
                except redis.RedisError as e:
                    logger.error(f"Erro no Redis durante transação segura: {e}")
                    return False
        return False
