"""
Implementação do algoritmo Radix Sort (LSD - Least Significant Digit).

Complexidade de Tempo: O(N * K), onde K é o número de dígitos da maior chave.
Complexidade de Espaço: O(N + Base) para os baldes auxiliares do counting sort.
Propriedade: Estável por definição de LSD.
Ideal para ordenação não-comparativa de números inteiros (IDs, anos, contadores).
"""

from typing import Any, Callable, Iterable, TypeVar

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

    Args:
        items: Elementos a ordenar.
        key: Função que mapeia cada item a um inteiro. Se None, o próprio item deve ser int.
        reverse: Se True, retorna em ordem decrescente mantendo a estabilidade relativa.
    """
    arr = list(items)
    if len(arr) <= 1:
        return arr

    key_fn: Callable[[T], int] = key if key is not None else (lambda x: int(x))

    # Para garantir estabilidade estrita mesmo com 'reverse=True' e inteiros de qualquer sinal,
    # associamos cada item com seu índice original (item, idx)
    # e ordenamos de forma crescente em relação a uma chave ajustada.
    min_val = min(key_fn(x) for x in arr)
    shift = -min_val if min_val < 0 else 0

    # Chave transladada para o conjunto dos inteiros não-negativos: shifted_key >= 0
    # Se reverse=True, queremos que a maior chave venha primeiro,
    # então usamos max_val - val como chave transladada não-negativa.
    max_val = max(key_fn(x) for x in arr)
    if reverse:
        get_shifted = lambda item: max_val - key_fn(item)
    else:
        get_shifted = lambda item: key_fn(item) + shift

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
        # Counting sort estável no dígito (current_val // exp) % 10
        output: list[T | None] = [None] * n
        count = [0] * 10

        for item in current:
            digito = (key_fn(item) // exp) % 10
            count[digito] += 1

        for i in range(1, 10):
            count[i] += count[i - 1]

        # Itera de trás para frente para preservar estritamente a estabilidade
        for i in range(n - 1, -1, -1):
            item = current[i]
            digito = (key_fn(item) // exp) % 10
            pos = count[digito] - 1
            output[pos] = item
            count[digito] -= 1

        current = [x for x in output if x is not None]
        exp *= 10

    return current
