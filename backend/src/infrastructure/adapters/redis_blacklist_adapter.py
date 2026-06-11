import logging

import redis

from application.ports.token_blacklist_provider import TokenBlacklistProvider

logger = logging.getLogger(__name__)


class RedisTokenBlacklistAdapter(TokenBlacklistProvider):
    """
    Adaptador de infraestrutura para gerenciar a blacklist de tokens no Redis.
    Implementa a porta TokenBlacklistProvider.
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "blacklist:token:"

    def adicionar_na_blacklist(self, token: str, expires_in_seconds: int) -> None:
        """
        Adiciona o token à blacklist usando o Redis.
        """
        try:
            chave = f"{self.prefix}{token}"
            # setex define o valor e o tempo de expiração de forma atômica
            self.redis.setex(name=chave, time=expires_in_seconds, value="revogado")
        except redis.RedisError as e:
            logger.error(f"Erro ao adicionar token à blacklist no Redis: {e}")

    def esta_na_blacklist(self, token: str) -> bool:
        """
        Verifica se a chave do token existe no Redis.
        Política Fail-Open: Se o Redis falhar, assume que NÃO está na blacklist
        para não bloquear o acesso legítimo, priorizando disponibilidade.
        """
        try:
            chave = f"{self.prefix}{token}"
            # exists retorna 1 se a chave existir, 0 caso contrário
            return self.redis.exists(chave) > 0
        except redis.RedisError as e:
            logger.error(f"Erro ao verificar blacklist no Redis: {e}")
            return False
