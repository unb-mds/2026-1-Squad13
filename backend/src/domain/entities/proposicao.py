from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Proposicao:
    id: str
    tipo: str
    numero: str
    ano: int
    ementa: str
    ementa_resumida: str
    autor: str
    orgao_origem: str
    status: str
    orgao_atual: str
    data_apresentacao: str
    data_ultima_movimentacao: str
    tempo_total_dias: int
    tem_atraso: bool
    tem_previsao_ia: bool
    tags: list[str] = field(default_factory=list)
    link_oficial: Optional[str] = None
    data_encerramento: Optional[str] = None
    previsao_aprovacao_dias: Optional[int] = None
