from enum import Enum

class ModoMovimentacao(str, Enum):
    RESUMIDO = "resumido"
    COMPLETO = "completo"
    RELEVANTE = "relevante"
