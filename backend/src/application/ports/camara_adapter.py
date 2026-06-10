from typing import Protocol

import httpx

from domain.entities.proposicao import Proposicao


class CamaraAdapterPort(Protocol):
    """
    Interface (Port) para o adaptador da API da Câmara dos Deputados.
    """

    async def buscar_por_id(
        self, id_proposicao: int, client: httpx.AsyncClient | None = None
    ) -> Proposicao | None:
        """Busca detalhes de uma proposição pelo seu ID."""
        ...

    async def listar_recentes(
        self,
        tipo: str,
        limite: int,
        ano: int | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> list[int]:
        """Lista IDs de proposições recentes."""
        ...

    async def buscar_id_por_identificacao(
        self,
        sigla_tipo: str,
        numero: str,
        ano: int,
        client: httpx.AsyncClient | None = None,
    ) -> int | None:
        """Busca o ID interno correspondente a um código canônico."""
        ...

    async def buscar_tramitacoes_brutas(
        self, id_proposicao: int, client: httpx.AsyncClient | None = None
    ) -> list[dict]:
        """Obtém o histórico de tramitações brutas da API."""
        ...

    async def coletar_em_lote(self, params: dict | None = None) -> list[Proposicao]:
        """Coleta proposições em lote."""
        ...

    async def obter_total(
        self, tipo: str, ano: int, client: httpx.AsyncClient | None = None
    ) -> int:
        """Obtém o total de proposições para um tipo e ano na API da Câmara."""
        ...
