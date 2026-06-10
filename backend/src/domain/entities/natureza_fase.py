from enum import StrEnum


class NaturezaFaseEnum(StrEnum):
    """
    Enum das naturezas de fase analítica.
    """

    OPERACIONAL = "operacional"
    HANDOFF = "handoff"
    TERMINAL = "terminal"
