from typing import Protocol, List
from src.domain.services.estimativa_aprovacao_service import (
    EstimativaAprovacaoService, 
    ResultadoEstimativa
)

class ProposicaoRepositoryInterface(Protocol):
    """
    Interface (Porta) para o repositório de proposições.
    Seguindo a inversão de dependência, a Aplicação define o que precisa.
    """
    def buscar_historico_dias_aprovacao(self, tipo: str, tema: str) -> List[int]:
        """Busca apenas os dias de tramitação de proposições similares já concluídas."""
        ...

class GerarEstimativaUseCase:
    """
    Caso de Uso: Orquestra a geração da estimativa.
    Responsável por buscar dados via infraestrutura e processar via domínio.
    """
    def __init__(self, repository: ProposicaoRepositoryInterface):
        self.repository = repository
        self.domain_service = EstimativaAprovacaoService()
        
    def executar(self, tipo: str, tema: str) -> ResultadoEstimativa:
        # 1. Busca dados históricos (Ação de Infraestrutura)
        historico_dias = self.repository.buscar_historico_dias_aprovacao(tipo, tema)
        
        # 2. Processa a regra de negócio (Ação de Domínio)
        return self.domain_service.calcular_estimativa(historico_dias)
