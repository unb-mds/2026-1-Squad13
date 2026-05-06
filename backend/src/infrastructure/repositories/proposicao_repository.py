from typing import List, Optional
from domain.entities.proposicao import Proposicao

class ProposicaoRepository:
    """
    Repositório temporário com dados em memória (Mock).
    No futuro, será substituído por uma implementação que acessa o banco de dados.
    """
    def __init__(self):
        self._dados = [
            Proposicao(
                id=1,
                tipo="PL",
                numero=123,
                ano=2024,
                autor="João Silva",
                uf_autor="DF",
                status_tramitacao="Em tramitação",
                ementa="Dispõe sobre transparência em processos públicos."
            ),
            Proposicao(
                id=2,
                tipo="PEC",
                numero=45,
                ano=2023,
                autor="Maria Souza",
                uf_autor="SP",
                status_tramitacao="Aprovada",
                ementa="Altera dispositivo constitucional sobre orçamento."
            ),
        ]

    def buscar_todos(self) -> List[Proposicao]:
        return self._dados

    def filtrar(
        self,
        tipo: Optional[str] = None,
        numero: Optional[int] = None,
        ano: Optional[int] = None,
        autor: Optional[str] = None,
        uf_autor: Optional[str] = None,
        status_tramitacao: Optional[str] = None
    ) -> List[Proposicao]:
        resultados = self._dados

        if tipo:
            resultados = [x for x in resultados if x.tipo.lower() == tipo.lower()]
        if numero:
            resultados = [x for x in resultados if x.numero == numero]
        if ano:
            resultados = [x for x in resultados if x.ano == ano]
        if autor:
            resultados = [x for x in resultados if autor.lower() in x.autor.lower()]
        if uf_autor:
            resultados = [x for x in resultados if x.uf_autor.lower() == uf_autor.lower()]
        if status_tramitacao:
            resultados = [
                x for x in resultados
                if x.status_tramitacao.lower() == status_tramitacao.lower()
            ]
        
        return resultados
