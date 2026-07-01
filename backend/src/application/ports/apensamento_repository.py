from typing import Protocol

from domain.entities.apensamento import Apensamento


class ApensamentoRepositoryPort(Protocol):
    """
    Interface (Port) para o repositório de Apensamentos.
    """

    def salvar(self, apensamento: Apensamento) -> Apensamento:
        """Salva um apensamento."""
        ...

    def buscar_por_materia_apensada(self, materia_id: str) -> Apensamento | None:
        """Busca um apensamento pelo ID da matéria apensada."""
        ...

    def buscar_por_materia_principal(self, materia_id: str) -> list[Apensamento]:
        """Busca apensamentos pelo ID da matéria principal."""
        ...
