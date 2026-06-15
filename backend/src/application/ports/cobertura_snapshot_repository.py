from typing import Protocol

from domain.entities.cobertura_snapshot import CoberturaSnapshot


class CoberturaSnapshotRepositoryPort(Protocol):
    """
    Interface (Port) para o repositório de CoberturaSnapshot.

    Todos os métodos de busca incluem `fonte` ("camara" | "senado") para garantir
    que snapshots de fontes distintas não sejam confundidos nem sobrescritos.
    """

    def salvar(self, snapshot: CoberturaSnapshot) -> CoberturaSnapshot:
        """Persiste um snapshot de cobertura (upsert por ano + tipo + fonte)."""
        ...

    def buscar_por_ano_tipo_e_fonte(
        self, ano: int, tipo_proposicao: str, fonte: str
    ) -> CoberturaSnapshot | None:
        """Busca o snapshot de cobertura correspondente ao ano, tipo e fonte."""
        ...

    def buscar_por_ano_e_tipo(
        self, ano: int, tipo_proposicao: str
    ) -> CoberturaSnapshot | None:
        """Busca o snapshot mais recente pelo ano e tipo (sem distinção de fonte).
        Mantido para retrocompatibilidade; prefira `buscar_por_ano_tipo_e_fonte`.
        """
        ...

    def buscar_todos(self) -> list[CoberturaSnapshot]:
        """Retorna todos os snapshots ordenados por data de atualização decrescente."""
        ...
