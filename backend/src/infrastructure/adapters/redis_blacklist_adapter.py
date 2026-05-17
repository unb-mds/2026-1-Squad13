import redis
from application.ports.token_blacklist_provider import TokenBlacklistProvider
from infrastructure.config import settings


class RedisTokenBlacklistAdapter(TokenBlacklistProvider):
    """
    Adaptador de infraestrutura para gerenciar a blacklist de tokens no Redis.
    Implementa a porta TokenBlacklistProvider.
    """

    def __init__(self, redis_client: redis.Redis = None):
        # Permite injetar um mock para testes, ou usa a conexão padrão
        if redis_client is None:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
            )
        else:
            self.redis = redis_client

        self.prefix = "blacklist:token:"

    def adicionar_na_blacklist(self, token: str, expires_in_seconds: int) -> None:
        """
        Adiciona o token à blacklist usando o Redis.

        [Conceito Pedagógico - Trade-off do TTL no Redis]:
        Delegar o gerenciamento do TTL (Time to Live) diretamente para o Redis 
        (via 'setex') é uma excelente escolha arquitetural porque:
        1. Desonera a aplicação de rodar CRON jobs ou rotinas em background para limpar tokens expirados.
        2. Otimiza o uso de memória do Redis automaticamente.
        3. A camada de infraestrutura cuida da mecânica de armazenamento, mantendo a
           lógica de "quanto tempo falta" estritamente no domínio/aplicação.
        """
        chave = f"{self.prefix}{token}"
        # setex define o valor e o tempo de expiração de forma atômica
        self.redis.setex(name=chave, time=expires_in_seconds, value="revogado")

    def esta_na_blacklist(self, token: str) -> bool:
        """
        Verifica se a chave do token existe no Redis.
        """
        chave = f"{self.prefix}{token}"
        # exists retorna 1 se a chave existir, 0 caso contrário
        return self.redis.exists(chave) > 0
