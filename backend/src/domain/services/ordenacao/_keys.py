"""
Helpers de comparação e estabilização de chaves para algoritmos de ordenação.
"""

from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class ReverseKey:
    """Encapsula um valor de chave para permitir ordenação inversa compatível com comparação."""

    __slots__ = ("obj",)

    def __init__(self, obj: Any) -> None:
        self.obj = obj

    def __lt__(self, other: "ReverseKey") -> bool:
        return other.obj < self.obj

    def __gt__(self, other: "ReverseKey") -> bool:
        return other.obj > self.obj

    def __le__(self, other: "ReverseKey") -> bool:
        return other.obj <= self.obj

    def __ge__(self, other: "ReverseKey") -> bool:
        return other.obj >= self.obj

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ReverseKey):
            return NotImplemented
        return self.obj == other.obj


def make_key_func(
    key: Callable[[T], Any] | None = None,
    reverse: bool = False,
) -> Callable[[T], Any]:
    """Retorna uma função de chave normalizada, suportando ou não inversão."""
    if key is None:
        if reverse:
            return lambda item: ReverseKey(item)
        return lambda item: item

    if reverse:
        return lambda item: ReverseKey(key(item))
    return key
