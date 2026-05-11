from abc import ABC, abstractmethod

from domain.entities.proposicao import Proposicao


class ProposicaoAdapter(ABC):
    @abstractmethod
    def buscar(self) -> list[Proposicao]:
        pass
