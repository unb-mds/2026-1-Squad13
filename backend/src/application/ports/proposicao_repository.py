from typing import Protocol

from domain.entities.proposicao import Proposicao


class ProposicaoRepositoryPort(Protocol):
    """
    Interface (Port) para o repositório de Proposições.
    """

    def salvar(self, proposicao: Proposicao) -> Proposicao:
        """Salva ou atualiza uma proposição no repositório."""
        ...

    def upsert_em_lote_por_numero_canonico(self, proposicoes: list[Proposicao]) -> None:
        """Executa um upsert em lote de proposições."""
        ...

    def buscar_por_id(self, id: str) -> Proposicao | None:
        """Busca uma proposição por ID."""
        ...

    def buscar_por_codigo(self, tipo: str, numero: str, ano: int) -> Proposicao | None:
        """Busca uma proposição pelo conjunto único Tipo, Número e Ano."""
        ...

    def filtrar(
        self,
        tipo: str | None = None,
        numero: str | None = None,
        ano: int | None = None,
        autor: str | None = None,
        uf_autor: str | None = None,
        status: str | None = None,
        busca: str | None = None,
        orgao_origem: str | None = None,
        data_inicio: str | None = None,
        data_fim: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Proposicao]:
        """Filtra proposições com base em critérios e paginação."""
        ...

    def contar(
        self,
        tipo: str | None = None,
        numero: str | None = None,
        ano: int | None = None,
        autor: str | None = None,
        uf_autor: str | None = None,
        status: str | None = None,
        busca: str | None = None,
        orgao_origem: str | None = None,
        data_inicio: str | None = None,
        data_fim: str | None = None,
    ) -> int:
        """Conta proposições que correspondem aos critérios."""
        ...

    def buscar_historico_dias_aprovacao(self, tipo: str, tema: str) -> list[int]:
        """Busca o tempo de tramitação de proposições concluídas por tipo e tema."""
        ...
