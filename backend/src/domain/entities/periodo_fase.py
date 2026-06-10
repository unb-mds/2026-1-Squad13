from datetime import date

from sqlmodel import SQLModel


class PeriodoFase(SQLModel):
    """
    Entidade de Domínio Pura para Períodos de Fase (periodo_fase).
    """

    id: int | None = None
    proposicao_id: str
    fase_analitica_id: int
    data_inicio: date
    data_fim: date | None = None
    duracao_dias: int | None = None
    recorrencia_numero: int = 1
    eh_fase_atual: bool = False
    motivo_travamento: str | None = None
    tipo_proposicao: str
    rito: str
    numero_turno: int | None = None
    subtipo_fase: str | None = None
    tipo_sessao: str | None = None
    origem_calculo: str
