from domain.entities.proposicao import Proposicao
from infrastructure.adapters.base_adapter import ProposicaoAdapter


class BuscarProposicoesService:
    def __init__(self, adapters: list[ProposicaoAdapter]) -> None:
        self._adapters = adapters

    def executar(
        self,
        filtros: dict,
        pagina: int,
        itens_por_pagina: int,
    ) -> dict:
        todas: list[Proposicao] = []
        for adapter in self._adapters:
            todas.extend(adapter.buscar())

        resultados = self._filtrar(todas, filtros)
        total = len(resultados)

        inicio = (pagina - 1) * itens_por_pagina
        items = resultados[inicio : inicio + itens_por_pagina]

        total_paginas = (total + itens_por_pagina - 1) // itens_por_pagina if itens_por_pagina > 0 else 0

        return {
            "items": items,
            "total": total,
            "pagina": pagina,
            "total_paginas": total_paginas,
        }

    def _filtrar(self, proposicoes: list[Proposicao], filtros: dict) -> list[Proposicao]:
        resultado = proposicoes

        busca = filtros.get("busca", "").strip().lower()
        if busca:
            resultado = [
                p for p in resultado
                if busca in p.ementa.lower()
                or busca in p.autor.lower()
                or busca in p.numero
                or any(busca in t.lower() for t in p.tags)
            ]

        if tipo := filtros.get("tipo", ""):
            resultado = [p for p in resultado if p.tipo == tipo]

        if status := filtros.get("status", ""):
            resultado = [p for p in resultado if p.status == status]

        if orgao := filtros.get("orgao_origem", ""):
            resultado = [p for p in resultado if p.orgao_origem == orgao]

        if data_inicio := filtros.get("data_inicio", ""):
            resultado = [p for p in resultado if p.data_apresentacao >= data_inicio]

        if data_fim := filtros.get("data_fim", ""):
            resultado = [p for p in resultado if p.data_apresentacao <= data_fim]

        return resultado
