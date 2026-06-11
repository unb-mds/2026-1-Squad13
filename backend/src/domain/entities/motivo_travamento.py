from enum import StrEnum


class MotivoTravamentoEnum(StrEnum):
    """
    Enum dos motivos de travamento em períodos de fase.
    """

    SOBRESTADO = "sobrestado"
    QUORUM = "quorum"
    PARECER_DIVERGENTE = "parecer_divergente"
    VINCULADA = "vinculada"
    PRIORIDADE_PRESIDENTE = "prioridade_presidente"
    OUTRO = "outro"
