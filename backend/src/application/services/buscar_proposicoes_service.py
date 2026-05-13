from infrastructure.repositories.proposicao_repository import ProposicaoRepository

class BuscarProposicoesService:
    """
    Serviço de Aplicação que orquestra a busca de proposições.
    Integra a lógica de filtros e paginação da 'main' com o repositório da 'develop'.
    """
    def __init__(self, repository: ProposicaoRepository):
        self.repository = repository

    def executar(
        self,
        filtros: dict,
        pagina: int = 1,
        itens_por_pagina: int = 10
    ) -> dict:
        
        # Regra de negócio legada da develop: pelo menos um filtro é obrigatório
        # (Ajustado para o novo formato de dicionário de filtros)
        valores_filtros = [filtros.get(k) for k in filtros]
        if not any(valor is not None and str(valor).strip() != "" for valor in valores_filtros):
            raise ValueError("Preencha pelo menos um filtro para realizar a busca.")

        filtros_repositorio = {
            "tipo": filtros.get("tipo"),
            "numero": filtros.get("numero"),
            "ano": filtros.get("ano"),
            "autor": filtros.get("autor"),
            "status": filtros.get("status"),
            "busca": filtros.get("busca"),
            "orgao_origem": filtros.get("orgao_origem"),
            "data_inicio": filtros.get("data_inicio"),
            "data_fim": filtros.get("data_fim"),
        }

        inicio = (pagina - 1) * itens_por_pagina

        total = self.repository.contar(**filtros_repositorio)

        items = self.repository.filtrar(
            **filtros_repositorio,
            limit=itens_por_pagina,
            offset=inicio,
        )

        total_paginas = (total + itens_por_pagina - 1) // itens_por_pagina if itens_por_pagina > 0 else 0

        return {
            "items": items,
            "total": total,
            "pagina": pagina,
            "total_paginas": total_paginas,
        }
