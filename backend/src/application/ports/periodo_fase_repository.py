from typing import Protocol
from domain.entities.periodo_fase import PeriodoFase


class PeriodoFaseRepositoryPort(Protocol):
    """
    Interface (Port) para o repositório de Períodos de Fase.
    """

    def salvar_lote(self, periodos: list[PeriodoFase]) -> list[PeriodoFase]:
        """Persiste uma lista de períodos em lote."""
        ...

    def buscar_por_proposicao(self, proposicao_id: str) -> list[PeriodoFase]:
        """Retorna todos os períodos de uma proposição ordenados cronologicamente."""
        ...

    def deletar_por_proposicao(self, proposicao_id: str) -> None:
        """Deleta todos os períodos de uma proposição."""
        ...
