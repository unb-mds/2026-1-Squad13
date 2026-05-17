from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ResultadoEstimativa:
    """Objeto de valor que representa o resultado do cálculo de domínio."""
    dias: Optional[int]
    status: str
    amostra: int

class EstimativaAprovacaoService:
    """
    Serviço de domínio puro para calcular a estimativa de aprovação.
    Regra central: Mínimo de 50 registros para garantir relevância estatística.
    """
    THRESHOLD_MINIMO_AMOSTRA = 50

    def calcular_estimativa(self, dias_historico: List[int]) -> ResultadoEstimativa:
        """
        Executa o cálculo baseado em uma lista de durações (em dias).
        """
        tamanho_amostra = len(dias_historico)
        
        if tamanho_amostra < self.THRESHOLD_MINIMO_AMOSTRA:
            return ResultadoEstimativa(
                dias=None,
                status="DADOS_INSUFICIENTES",
                amostra=tamanho_amostra
            )
            
        # Para o MVP, usamos a média aritmética. 
        # No futuro, este método pode evoluir para usar modelos de ML ou Mediana 
        # sem afetar o restante do sistema.
        if tamanho_amostra == 0: # Segurança contra divisão por zero, embora o threshold trate
             return ResultadoEstimativa(dias=None, status="DADOS_INSUFICIENTES", amostra=0)

        media_dias = sum(dias_historico) // tamanho_amostra
        
        return ResultadoEstimativa(
            dias=media_dias,
            status="CALCULADA",
            amostra=tamanho_amostra
        )
