from typing import Protocol

from domain.entities.evento_tramitacao import EventoTramitacao


class EventoTramitacaoRepositoryPort(Protocol):
    """
    Interface (Port) para o repositório de Eventos de Tramitação.
    """

    def salvar(self, evento: EventoTramitacao) -> EventoTramitacao:
        """Persiste um único evento de tramitação."""
        ...

    def salvar_lote(self, eventos: list[EventoTramitacao]) -> list[EventoTramitacao]:
        """Persiste uma lista de eventos em lote."""
        ...

    def existe_algum_evento(self, proposicao_id: str) -> bool:
        """Verifica se existe pelo menos um evento para a proposição."""
        ...

    def buscar_por_proposicao(
        self, proposicao_id: str, somente_relevantes: bool = False
    ) -> list[EventoTramitacao]:
        """Retorna eventos de uma proposição ordenados cronologicamente."""
        ...

    def buscar_por_multiplas_proposicoes(
        self, proposicoes_ids: list[str]
    ) -> dict[str, list[EventoTramitacao]]:
        """Retorna eventos para múltiplas proposições de uma só vez (batch query)."""
        ...

    def buscar_ultimo_evento(self, proposicao_id: str) -> EventoTramitacao | None:
        """Retorna o evento mais recente de uma proposição."""
        ...

    def deletar_por_proposicao(self, proposicao_id: str) -> None:
        """Remove todos os eventos de uma proposição."""
        ...

    def contar_por_tipo(self, proposicao_id: str) -> dict[str, int]:
        """Retorna contagem de eventos agrupados por tipo_evento."""
        ...
