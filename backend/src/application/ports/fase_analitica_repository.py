from typing import Protocol

from domain.entities.fase_analitica import FaseAnalitica


class FaseAnaliticaRepositoryPort(Protocol):
    """
    Interface (Port) para o repositório de Fases Analíticas.
    """

    def buscar_por_codigo(self, codigo: str) -> FaseAnalitica | None:
        """Busca uma fase pelo seu código único."""
        ...

    def buscar_todas(self) -> list[FaseAnalitica]:
        """Lista todas as fases ordenadas por ordem_logica."""
        ...

    def seed_fases(self) -> None:
        """Executa o seed idempotente das fases."""
        ...
