from dataclasses import dataclass
from typing import Optional

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

    @property
    def nome_canonico(self) -> str:
        """Exemplo: PL 123/2024"""
        return f"{self.tipo} {self.numero}/{self.ano}"
