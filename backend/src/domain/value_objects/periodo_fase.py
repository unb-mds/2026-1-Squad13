from dataclasses import dataclass
from datetime import date

from ..entities.evento_tramitacao import EventoTramitacao


@dataclass
class PeriodoFase:
    fase_codigo: str  # ex: "ANALISE_COMISSOES"
    fase_nome: str  # ex: "Análise em comissões"
    ordem_logica: int  # 1–8
    data_entrada: date
    data_saida: date | None  # None se fase ainda ativa
    dias_corridos: int
    eventos_relevantes: list[EventoTramitacao]
    ocorrencia: int  # 1ª, 2ª, 3ª vez nessa fase (para fases repetidas)
    motivo_travamento: str | None = None
    numero_turno: int | None = None
    subtipo_fase: str | None = None
