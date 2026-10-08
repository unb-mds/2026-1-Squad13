"""
Implementação do algoritmo Radix Sort (LSD - Least Significant Digit).

Complexidade de Tempo: O(N * K), onde K é o número de dígitos da maior chave.
Complexidade de Espaço: O(N + Base) para os baldes auxiliares do counting sort.
Propriedade: Estável por definição de LSD.
Ideal para ordenação não-comparativa de números inteiros (IDs, anos, contadores).
"""

from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")


def radix_sort(
    items: Iterable[T],
    *,
    key: Callable[[T], int] | None = None,
    reverse: bool = False,
) -> list[T]:
    """
    Ordena uma coleção com base em chaves inteiras utilizando Radix Sort LSD.
    Suporta inteiros positivos, negativos e zero, com garantia rigorosa de estabilidade.
    """
    arr = list(items)
    if len(arr) <= 1:
        return arr

    key_fn: Callable[[T], int] = key if key is not None else int

    min_val = min(key_fn(x) for x in arr)
    shift = -min_val if min_val < 0 else 0
    max_val = max(key_fn(x) for x in arr)

    if reverse:

        def get_shifted(item: T) -> int:
            return max_val - key_fn(item)

    else:

        def get_shifted(item: T) -> int:
            return key_fn(item) + shift

    return _radix_sort_non_negative(arr, get_shifted)


def _radix_sort_non_negative(items: list[T], key_fn: Callable[[T], int]) -> list[T]:
    """Ordena itens com chaves inteiras >= 0 utilizando Counting Sort estável dígito a dígito."""
    if len(items) <= 1:
        return list(items)

    max_val = max(key_fn(x) for x in items)
    if max_val == 0:
        return list(items)

    exp = 1
    current = list(items)
    n = len(current)

    while max_val // exp > 0:
        output: list[T | None] = [None] * n
        count = [0] * 10

        for item in current:
            digito = (key_fn(item) // exp) % 10
            count[digito] += 1

        for i in range(1, 10):
            count[i] += count[i - 1]

        for i in range(n - 1, -1, -1):
            item = current[i]
            digito = (key_fn(item) // exp) % 10
            pos = count[digito] - 1
            output[pos] = item
            count[digito] -= 1

        current = [x for x in output if x is not None]
        exp *= 10

    return current
