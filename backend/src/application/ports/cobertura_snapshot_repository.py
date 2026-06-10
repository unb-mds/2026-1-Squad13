from typing import Protocol
from domain.entities.cobertura_snapshot import CoberturaSnapshot


class CoberturaSnapshotRepositoryPort(Protocol):
    """
    Interface (Port) para o repositório de CoberturaSnapshot.
    """

    def salvar(self, snapshot: CoberturaSnapshot) -> CoberturaSnapshot:
        """Persiste um snapshot de cobertura."""
        ...

    def buscar_por_ano_e_tipo(self, ano: int, tipo_proposicao: str) -> CoberturaSnapshot | None:
        """Busca o snapshot de cobertura correspondente ao ano e tipo."""
        ...

    def buscar_todos(self) -> list[CoberturaSnapshot]:
        """Retorna todos os snapshots ordenados por data de atualização descrescente."""
        ...
