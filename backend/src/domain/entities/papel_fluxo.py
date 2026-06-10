from enum import StrEnum


class PapelFluxoEnum(StrEnum):
    """
    Enum dos papéis no fluxo de fase analítica.
    """

    ENTRADA = "entrada"
    PERMANENCIA = "permanencia"
    TRANSICAO = "transicao"
    SAIDA = "saida"
    TERMINAL = "terminal"
