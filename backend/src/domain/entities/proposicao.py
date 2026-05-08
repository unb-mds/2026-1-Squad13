from dataclasses import dataclass, field
from typing import Optional, List

@dataclass(frozen=True)
class Proposicao:
    """
    Entidade de Domínio que representa um Projeto de Lei (PL) ou similar.
    Esta classe é independente de frameworks ou APIs externas.
    """
    id: Optional[int]
    tipo: str
    numero: int
    ano: int
    autor: str
    uf_autor: str
    status_tramitacao: str
    ementa: str
    data_apresentacao: str
    data_ultima_movimentacao: str
    orgao_atual: str
    link_oficial: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    @property
    def nome_canonico(self) -> str:
        """Exemplo: PL 123/2024"""
        return f"{self.tipo} {self.numero}/{self.ano}"
