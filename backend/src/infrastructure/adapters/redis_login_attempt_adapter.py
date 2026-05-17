import logging
import redis
from domain.services.login_attempt_service import LoginAttemptProvider
from infrastructure.config import settings

logger = logging.getLogger(__name__)


class RedisLoginAttemptAdapter(LoginAttemptProvider):
    """
    Implementação da interface LoginAttemptProvider usando Redis.
    Armazena o contador de falhas com um tempo de expiração (TTL).
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "login_attempts:"
        self.ttl = settings.BLOQUEIO_MINUTOS * 60  # Converte minutos para segundos
        self.max_attempts = settings.TENTATIVAS_MAXIMAS

    def _get_key(self, email: str) -> str:
        return f"{self.prefix}{email}"

    def registrar_falha(self, email: str) -> int:
        """
        Incrementa o contador de falhas para o email informado.
        Política Fail-Open: Se o Redis falhar, loga o erro e retorna 0 (não bloqueia).
        """
        try:
            key = self._get_key(email)
            attempts = self.redis.incr(key)

            # Define a expiração apenas na primeira falha ou se a chave não tiver TTL
            if attempts == 1:
                self.redis.expire(key, self.ttl)

            return attempts
        except redis.RedisError as e:
            logger.error(f"Erro ao registrar falha de login no Redis para {email}: {e}")
            return 0

    def esta_bloqueado(self, email: str) -> bool:
        """
        Verifica se o número de tentativas excedeu o limite configurado.
        Política Fail-Open: Se o Redis falhar, assume que não está bloqueado.
        """
        try:
            key = self._get_key(email)
            attempts = self.redis.get(key)

            if attempts is None:
                return False

            return int(attempts) >= self.max_attempts
        except (redis.RedisError, ValueError) as e:
            logger.error(f"Erro ao verificar bloqueio no Redis para {email}: {e}")
            return False

    def resetar_tentativas(self, email: str) -> None:
        """
        Remove a chave do Redis, limpando o histórico de falhas.
        """
        try:
            key = self._get_key(email)
            self.redis.delete(key)
        except redis.RedisError as e:
            logger.error(f"Erro ao resetar tentativas no Redis para {email}: {e}")

    def tempo_restante_bloqueio(self, email: str) -> int:
        """
        Retorna o TTL da chave no Redis em segundos.
        """
        try:
            key = self._get_key(email)
            ttl = self.redis.ttl(key)
            return max(0, ttl) if ttl > 0 else 0
        except redis.RedisError as e:
            logger.error(f"Erro ao buscar TTL no Redis para {email}: {e}")
            return 0
