from collections.abc import Callable
from typing import Any, Protocol


class CacheProvider(Protocol):
    """
    Interface para o provedor de cache.
    Permite desacoplar a camada de Aplicação da biblioteca de infraestrutura (ex: Redis).
    """

    def get(self, key: str) -> Any | None:
        """Recupera um valor do cache."""
        ...

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Salva um valor no cache com um tempo de vida (TTL) opcional."""
        ...

    def delete(self, key: str) -> None:
        """Remove um valor específico do cache."""
        ...

    def invalidate(self, prefix: str) -> None:
        """Invalida todas as chaves que começam com o prefixo fornecido."""
        ...

    def set_nx(self, key: str, value: Any, ttl_seconds: int) -> bool:
        """Salva no cache apenas se a chave não existir. Retorna True se criada."""
        ...

    def eval_lua(self, script: str, keys: list[str], args: list[Any]) -> Any:
        """Executa um script Lua atômico no provedor de cache."""
        ...

    def obter_e_atualizar_multichaves_seguro(
        self, keys: list[str], update_fn: Callable[[list[Any]], dict[str, Any] | None]
    ) -> bool:
        """Executa uma atualização transacional segura (Optimistic Locking) em múltiplas chaves."""
        ...


