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
    Regra central: Mínimo de registros para garantir relevância estatística.
    """

    def __init__(self, threshold_minimo_amostra: int = 50):
        self.threshold_minimo_amostra = threshold_minimo_amostra

    def calcular_estimativa(self, dias_historico: List[int]) -> ResultadoEstimativa:
        """
        Executa o cálculo baseado em uma lista de durações (em dias).
        """
        tamanho_amostra = len(dias_historico)

        if tamanho_amostra < self.threshold_minimo_amostra:
            return ResultadoEstimativa(
                dias=None, status="DADOS_INSUFICIENTES", amostra=tamanho_amostra
            )

        # Para o MVP, usamos a média aritmética.
        # No futuro, este método pode evoluir para usar modelos de ML ou Mediana
        # sem afetar o restante do sistema.
        if (
            tamanho_amostra == 0
        ):  # Segurança contra divisão por zero, embora o threshold trate
            return ResultadoEstimativa(
                dias=None, status="DADOS_INSUFICIENTES", amostra=0
            )

        media_dias = sum(dias_historico) // tamanho_amostra

        return ResultadoEstimativa(
            dias=media_dias, status="CALCULADA", amostra=tamanho_amostra
        )
