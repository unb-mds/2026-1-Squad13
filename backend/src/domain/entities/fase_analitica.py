from sqlmodel import SQLModel


class FaseAnalitica(SQLModel):
    """
    Entidade de Domínio para Fase Analítica.
    """

    id: int | None = None
    codigo: str
    nome: str
    ordem_logica: int
    natureza: str = "operacional"
    papel_fluxo: str = "permanencia"
    permite_estoque_atual: bool = True
    permite_metricas_tempo: bool = True
    indica_fase_terminal: bool = False
    justificativa_juridica: str = ""


# Constantes para uso interno — evita strings mágicas no código
FASES_SEED = [
    {
        "codigo": "PROTOCOLO_INICIAL",
        "nome": "Protocolo inicial",
        "ordem_logica": 1,
        "natureza": "operacional",
        "papel_fluxo": "entrada",
        "permite_estoque_atual": True,
        "permite_metricas_tempo": True,
        "indica_fase_terminal": False,
        "justificativa_juridica": "Início formal da tramitação.",
    },
    {
        "codigo": "ANALISE_COMISSOES",
        "nome": "Análise em comissões",
        "ordem_logica": 2,
        "natureza": "operacional",
        "papel_fluxo": "permanencia",
        "permite_estoque_atual": True,
        "permite_metricas_tempo": True,
        "indica_fase_terminal": False,
        "justificativa_juridica": "Distribuição e análise por comissões.",
    },
    {
        "codigo": "AGUARDANDO_PAUTA",
        "nome": "Aguardando pauta",
        "ordem_logica": 3,
        "natureza": "operacional",
        "papel_fluxo": "permanencia",
        "permite_estoque_atual": True,
        "permite_metricas_tempo": True,
        "indica_fase_terminal": False,
        "justificativa_juridica": "Inclusão formal em pauta deliberativa.",
    },
    {
        "codigo": "DELIBERACAO_PLENARIO",
        "nome": "Deliberação em plenário",
        "ordem_logica": 4,
        "natureza": "operacional",
        "papel_fluxo": "saida",
        "permite_estoque_atual": True,
        "permite_metricas_tempo": True,
        "indica_fase_terminal": False,
        "justificativa_juridica": "Deliberação decisiva pelo Plenário.",
    },
    {
        "codigo": "TRAMITE_ENTRE_CASAS",
        "nome": "Trâmite entre Casas",
        "ordem_logica": 5,
        "natureza": "handoff",
        "papel_fluxo": "transicao",
        "permite_estoque_atual": False,
        "permite_metricas_tempo": True,
        "indica_fase_terminal": False,
        "justificativa_juridica": "Handoff bicameral físico/digital.",
    },
    {
        "codigo": "REVISAO_OUTRA_CASA",
        "nome": "Revisão na outra Casa",
        "ordem_logica": 6,
        "natureza": "operacional",
        "papel_fluxo": "permanencia",
        "permite_estoque_atual": True,
        "permite_metricas_tempo": True,
        "indica_fase_terminal": False,
        "justificativa_juridica": "Deliberação na Casa revisora.",
    },
    {
        "codigo": "ETAPA_EXECUTIVO",
        "nome": "Etapa no Executivo",
        "ordem_logica": 7,
        "natureza": "operacional",
        "papel_fluxo": "saida",
        "permite_estoque_atual": True,
        "permite_metricas_tempo": True,
        "indica_fase_terminal": False,
        "justificativa_juridica": "Remessa para sanção ou veto presidencial.",
    },
    {
        "codigo": "ENCERRADA",
        "nome": "Encerrada",
        "ordem_logica": 8,
        "natureza": "terminal",
        "papel_fluxo": "terminal",
        "permite_estoque_atual": False,
        "permite_metricas_tempo": False,
        "indica_fase_terminal": True,
        "justificativa_juridica": "Conclusão definitiva da tramitação.",
    },
]
