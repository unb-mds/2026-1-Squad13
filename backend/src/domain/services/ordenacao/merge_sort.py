"""
Implementação do algoritmo Merge Sort com garantia estrita de estabilidade.

Complexidade de Tempo: O(N log N) em todos os casos (melhor, médio e pior).
Complexidade de Espaço Adicional: O(N) para particionamento e mescla.
Propriedade: Estável (mantém a ordem relativa de elementos com chaves iguais).
"""

from collections.abc import Callable, Iterable
from typing import Any, TypeVar

from ._keys import make_key_func

T = TypeVar("T")


def merge_sort(
    items: Iterable[T],
    *,
    key: Callable[[T], Any] | None = None,
    reverse: bool = False,
) -> list[T]:
    """
    Ordena uma sequência iterável utilizando Merge Sort de forma puramente estável.

    Args:
        items: Coleção de elementos a serem ordenados.
        key: Função opcional para extração da chave de comparação.
        reverse: Se True, ordena em ordem decrescente mantendo a estabilidade relativa.

    Returns:
        Uma nova lista com os elementos ordenados.
    """
    arr = list(items)
    if len(arr) <= 1:
        return arr

    key_fn = make_key_func(key=key, reverse=reverse)

    # Vetor auxiliar de tuplas (chave_calculada, item) para não recalcular key() repetidamente
    tagged = [(key_fn(x), x) for x in arr]
    _merge_sort_rec(tagged, 0, len(tagged))
    return [item for _, item in tagged]


def _merge_sort_rec(arr: list[tuple[Any, T]], left: int, right: int) -> None:
    """Função recursiva do Merge Sort operando no intervalo [left, right)."""
    if right - left <= 1:
        return

    mid = left + (right - left) // 2
    _merge_sort_rec(arr, left, mid)
    _merge_sort_rec(arr, mid, right)
    _merge(arr, left, mid, right)


def _merge(arr: list[tuple[Any, T]], left: int, mid: int, right: int) -> None:
    """Intercala duas fatias ordenadas mantendo estritamente a estabilidade (<=)."""
    left_slice = arr[left:mid]
    right_slice = arr[mid:right]

    i = 0
    j = 0
    k = left
    len_left = len(left_slice)
    len_right = len(right_slice)

    # O uso de '<=' garante a estabilidade: se forem iguais, o elemento da esquerda é preferido
    while i < len_left and j < len_right:
        if left_slice[i][0] <= right_slice[j][0]:
            arr[k] = left_slice[i]
            i += 1
        else:
            arr[k] = right_slice[j]
            j += 1
        k += 1

    while i < len_left:
        arr[k] = left_slice[i]
        i += 1
        k += 1

    while j < len_right:
        arr[k] = right_slice[j]
        j += 1
        k += 1
