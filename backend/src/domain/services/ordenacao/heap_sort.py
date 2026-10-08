"""
Implementação do algoritmo Heap Sort.

Complexidade de Tempo: O(N log N) em todos os casos (melhor, médio e pior).
Complexidade de Espaço: O(1) in-place no array transformado (ou O(N) com cópia e desempate estável).
Para assegurar paridade estrita com o comportamento estável de sorted() no LexTrack,
a ordenação utiliza tuplas com índice de inserção original (chave, idx).
"""

from typing import Any, Callable, Iterable, TypeVar

from ._keys import make_key_func

T = TypeVar("T")


def heap_sort(
    items: Iterable[T],
    *,
    key: Callable[[T], Any] | None = None,
    reverse: bool = False,
) -> list[T]:
    """
    Ordena uma coleção utilizando Heap Sort.
    Para garantir previsibilidade total em empates de chaves iguais,
    utiliza ordenação estabilizada por índice original.

    Args:
        items: Coleção a ser ordenada.
        key: Função opcional para extração da chave de comparação.
        reverse: Se True, ordena em ordem decrescente.
    """
    arr = list(items)
    n = len(arr)
    if n <= 1:
        return arr

    key_fn = make_key_func(key=key, reverse=reverse)

    # Cada elemento vira ((chave_normalizada, idx_original), item)
    # Como o Heap Sort padrão constrói Max-Heap e coloca no fim,
    # a comparação natural de tuplas garante estabilidade.
    tagged = [((key_fn(item), i), item) for i, item in enumerate(arr)]

    # Constrói o Max-Heap (heapify bottom-up)
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(tagged, n, i)

    # Extrai elementos do heap um a um
    for i in range(n - 1, 0, -1):
        tagged[0], tagged[i] = tagged[i], tagged[0]
        _sift_down(tagged, i, 0)

    return [item for _, item in tagged]


def _sift_down(arr: list[tuple[tuple[Any, int], T]], n: int, root: int) -> None:
    """Afunda o nó 'root' no heap de tamanho 'n' para manter a propriedade de Max-Heap."""
    largest = root
    left = 2 * root + 1
    right = 2 * root + 2

    if left < n and arr[left][0] > arr[largest][0]:
        largest = left

    if right < n and arr[right][0] > arr[largest][0]:
        largest = right

    if largest != root:
        arr[root], arr[largest] = arr[largest], arr[root]
        _sift_down(arr, n, largest)
