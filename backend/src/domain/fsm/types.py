from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class House(StrEnum):
    CAMARA = "Câmara"
    SENADO = "Senado"


class StepRole(StrEnum):
    ORIGEM = "origem"
    REVISORA = "revisora"
    RETORNO = "retorno"


class InputType(StrEnum):
    GATILHO_REMESSA = "GATILHO_REMESSA"
    GATILHO_RETORNO = "GATILHO_RETORNO"
    EXCLUSIVO_CAMARA = "EXCLUSIVO_CÂMARA"
    EXCLUSIVO_SENADO = "EXCLUSIVO_SENADO"
    AMBIGUO_OU_NEUTRO = "AMBÍGUO_OU_NEUTRO"


@dataclass(frozen=True)
class EventData:
    timestamp: datetime
    sigla_orgao: str
    orgao_nome: str
    descricao: str
    remessa_ou_retorno: str | None


@dataclass
class FSMState:
    casa_ativa: House
    tipo_passo: StepRole
    timestamp_entrada: datetime
    casa_origem: House
    ultima_casa_nao_ambigua: House
    ja_passou_pela_revisora: bool
    ultimo_gatilho_foi_implicito: bool


@dataclass
class TransitStep:
    casa: House
    tipo_passo: StepRole
    data_entrada: datetime
    data_saida: datetime | None = None
    duracao_dias: int = 0
