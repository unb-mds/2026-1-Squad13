"""
Implementação do algoritmo Quick Sort com pivô por Mediana de Três.

Complexidade de Tempo: O(N log N) no caso médio; mitigação do pior caso O(N^2)
através da escolha do pivô pela mediana entre início, meio e fim.
Para manter equivalência determinística com sorted() do LexTrack,
elementos possuem empates resolvidos pelo índice original de inserção.
"""

from collections.abc import Callable, Iterable
from typing import Any, TypeVar

from ._keys import make_key_func

T = TypeVar("T")


def quick_sort(
    items: Iterable[T],
    *,
    key: Callable[[T], Any] | None = None,
    reverse: bool = False,
) -> list[T]:
    """
    Ordena uma coleção utilizando Quick Sort com particionamento de Hoare
    e escolha de pivô por mediana de três.

    Args:
        items: Coleção de elementos a serem ordenados.
        key: Função opcional para extração da chave.
        reverse: Se True, ordena em ordem decrescente.
    """
    arr = list(items)
    n = len(arr)
    if n <= 1:
        return arr

    key_fn = make_key_func(key=key, reverse=reverse)

    # Associa com índice original para manter comportamento estável em empates
    tagged = [((key_fn(item), i), item) for i, item in enumerate(arr)]

    _quick_sort_rec(tagged, 0, n - 1)
    return [item for _, item in tagged]


def _quick_sort_rec(arr: list[tuple[tuple[Any, int], T]], low: int, high: int) -> None:
    """QuickSort recursivo operando no intervalo [low, high]."""
    if low < high:
        # Se partição pequena (<= 10), poderíamos usar insertion,
        # mas mantemos particionamento direto
        pivot_idx = _partition(arr, low, high)
        _quick_sort_rec(arr, low, pivot_idx)
        _quick_sort_rec(arr, pivot_idx + 1, high)


def _median_of_three(arr: list[tuple[tuple[Any, int], T]], low: int, high: int) -> tuple[Any, int]:
    """Calcula o pivô utilizando a mediana de três (primeiro, meio, último)."""
    mid = low + (high - low) // 2
    a = arr[low][0]
    b = arr[mid][0]
    c = arr[high][0]

    # Encontra a mediana entre a, b, c
    if (a <= b <= c) or (c <= b <= a):
        return b
    elif (b <= a <= c) or (c <= a <= b):
        return a
    else:
        return c


def _partition(arr: list[tuple[tuple[Any, int], T]], low: int, high: int) -> int:
    """Particionamento de Hoare com pivô por mediana de 3."""
    pivot = _median_of_three(arr, low, high)
    i = low - 1
    j = high + 1

    while True:
        i += 1
        while arr[i][0] < pivot:
            i += 1

        j -= 1
        while arr[j][0] > pivot:
            j -= 1

        if i >= j:
            return j

        arr[i], arr[j] = arr[j], arr[i]
