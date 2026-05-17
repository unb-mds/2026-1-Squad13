from typing import Protocol, Any, Optional

class CacheProvider(Protocol):
    """
    Interface para o provedor de cache.
    Permite desacoplar a camada de Aplicação da biblioteca de infraestrutura (ex: Redis).
    """

    def get(self, key: str) -> Optional[Any]:
        """Recupera um valor do cache."""
        ...

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Salva um valor no cache com um tempo de vida (TTL) opcional."""
        ...

    def delete(self, key: str) -> None:
        """Remove um valor específico do cache."""
        ...

    def invalidate(self, prefix: str) -> None:
        """Invalida todas as chaves que começam com o prefixo fornecido."""
        ...
