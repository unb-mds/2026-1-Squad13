
from sqlmodel import SQLModel


class FaseAnalitica(SQLModel):
    """
    Entidade de Domínio para Fase Analítica.
    """

    id: int | None = None
    codigo: str
    nome: str
    ordem_logica: int


# Constantes para uso interno — evita strings mágicas no código
FASES_SEED = [
    {"codigo": "PROTOCOLO_INICIAL", "nome": "Protocolo inicial", "ordem_logica": 1},
    {"codigo": "ANALISE_COMISSOES", "nome": "Análise em comissões", "ordem_logica": 2},
    {"codigo": "AGUARDANDO_PAUTA", "nome": "Aguardando pauta", "ordem_logica": 3},
    {
        "codigo": "DELIBERACAO_PLENARIO",
        "nome": "Deliberação em plenário",
        "ordem_logica": 4,
    },
    {
        "codigo": "TRAMITE_ENTRE_CASAS",
        "nome": "Trâmite entre Casas",
        "ordem_logica": 5,
    },
    {
        "codigo": "REVISAO_OUTRA_CASA",
        "nome": "Revisão na outra Casa",
        "ordem_logica": 6,
    },
    {"codigo": "ETAPA_EXECUTIVO", "nome": "Etapa no Executivo", "ordem_logica": 7},
    {"codigo": "ENCERRADA", "nome": "Encerrada", "ordem_logica": 8},
]
