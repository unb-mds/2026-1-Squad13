import redis
from domain.services.login_attempt_service import LoginAttemptProvider
from infrastructure.config import settings


class RedisLoginAttemptAdapter(LoginAttemptProvider):
    """
    Implementação da interface LoginAttemptProvider usando Redis.
    Armazena o contador de falhas com um tempo de expiração (TTL).
    """

    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        self.prefix = "login_attempts:"
        self.ttl = settings.BLOQUEIO_MINUTOS * 60  # Converte minutos para segundos
        self.max_attempts = settings.TENTATIVAS_MAXIMAS

    def _get_key(self, email: str) -> str:
        return f"{self.prefix}{email}"

    def registrar_falha(self, email: str) -> int:
        """
        Incrementa o contador de falhas para o email informado.
        Define o TTL (Time to Live) para garantir o bloqueio temporário.
        """
        key = self._get_key(email)
        attempts = self.redis.incr(key)

        # Define a expiração apenas na primeira falha ou se a chave não tiver TTL
        if attempts == 1:
            self.redis.expire(key, self.ttl)

        return attempts

    def esta_bloqueado(self, email: str) -> bool:
        """
        Verifica se o número de tentativas excedeu o limite configurado.
        """
        key = self._get_key(email)
        attempts = self.redis.get(key)

        if attempts is None:
            return False

        return int(attempts) >= self.max_attempts

    def resetar_tentativas(self, email: str) -> None:
        """
        Remove a chave do Redis, limpando o histórico de falhas.
        """
        key = self._get_key(email)
        self.redis.delete(key)
