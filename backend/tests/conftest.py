import pytest
from domain.entities.proposicao import Proposicao

@pytest.fixture
def proposicao_exemplo():
    """Entidade válida reutilizável em qualquer teste."""
    return Proposicao(
        id="12345",
        tipo="PL",
        numero="123",
        ano=2024,
        autor="Autor Exemplo",
        uf_autor="DF",
        status="Em tramitação",
        ementa="Dispõe sobre exemplo de teste",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        orgao_atual="CCJ",
        tags=[]
    )

@pytest.fixture
def lista_proposicoes(proposicao_exemplo):
    """Lista com 3 proposições para testar paginação/filtros."""
    return [
        proposicao_exemplo,
        Proposicao(
            id="12346",
            tipo="PEC",
            numero="45",
            ano=2023,
            autor="Autor 2",
            uf_autor="SP",
            status="Aprovada",
            ementa="Outra proposta",
            data_apresentacao="2023-01-01",
            data_ultima_movimentacao="2023-12-01",
            orgao_atual="Plenário",
            tags=[]
        ),
        Proposicao(
            id="12347",
            tipo="PL",
            numero="124",
            ano=2024,
            autor="Autor 3",
            uf_autor="RJ",
            status="Em tramitação",
            ementa="Mais uma",
            data_apresentacao="2024-02-01",
            data_ultima_movimentacao="2024-02-01",
            orgao_atual="Mesa",
            tags=[]
        ),
    ]
