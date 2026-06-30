import re

from .types import EventData, InputType

PADROES_REMESSA: list[re.Pattern] = [
    re.compile(
        r"(remessa|remetido|envio|ofício.*encaminhando.*autógrafo).*senado",
        re.IGNORECASE,
    ),
    re.compile(r"remessa ao senado federal", re.IGNORECASE),
]

PADROES_RETORNO_SENADO: list[re.Pattern] = [
    re.compile(r"^(remetida|remessa)[\s\S]*câmara", re.IGNORECASE),
    re.compile(r"^(ofício|comunicação)[\s\S]*câmara", re.IGNORECASE),
]

PADROES_RETORNO_CAMARA: list[re.Pattern] = [
    re.compile(
        r"^(recebido\s+o\s+ofício|recebimento\s+do\s+ofício|recebido)[\s\S]*senado",
        re.IGNORECASE,
    ),
    re.compile(r"^retorno[\s\S]*senado", re.IGNORECASE),
]

SIGLAS_EXCLUSIVAS_SENADO = {
    "ccj",
    "cae",
    "cas",
    "cra",
    "cre",
    "ci",
    "cdh",
    "cma",
    "csp",
    "ctfc",
    "cdr",
    "sexpe",
    "ssclsf",
    "slsf",
    "seadi",
    "sacdh",
    "sace",
    "saccj",
    "sacas",
    "sacae",
    "sacma",
    "sacsp",
    "sacra",
    "sacifr",
    "sacct",
    "sacdr",
    "sactfc",
}

SIGLAS_EXCLUSIVAS_CAMARA = {
    "ccjc",
    "cft",
    "ccjr",
    "ccp",
    "cpasf",
    "csaude",
    "cult",
    "ctrab",
    "cde",
    "cvt",
    "cidoso",
}


def classify_event(event: EventData) -> InputType:
    desc = event.descricao or ""
    sigla = (event.sigla_orgao or "").lower().strip()
    orgao_lower = (event.orgao_nome or "").lower()

    # 1. Verificar gatilhos explícitos
    if event.remessa_ou_retorno == "REMESSA":
        return InputType.GATILHO_REMESSA
    if event.remessa_ou_retorno == "RETORNO":
        return InputType.GATILHO_RETORNO

    # Regexes para remessa
    for pattern in PADROES_REMESSA:
        if pattern.search(desc):
            return InputType.GATILHO_REMESSA

    # Regexes para retorno
    for pattern in PADROES_RETORNO_SENADO:
        if pattern.search(desc):
            return InputType.GATILHO_RETORNO
    for pattern in PADROES_RETORNO_CAMARA:
        if pattern.search(desc):
            return InputType.GATILHO_RETORNO

    # 2. Localidades exclusivas
    e_exclusivo_senado = (
        sigla == "sf"
        or sigla == "slsf"
        or sigla == "ssclsf"
        or "sf" in orgao_lower
        or "senado" in orgao_lower
        or sigla in SIGLAS_EXCLUSIVAS_SENADO
    )

    if e_exclusivo_senado:
        return InputType.EXCLUSIVO_SENADO

    if sigla in SIGLAS_EXCLUSIVAS_CAMARA or (
        len(sigla) >= 4 and sigla.startswith("c") and not sigla.startswith("sa")
    ):
        return InputType.EXCLUSIVO_CAMARA

    return InputType.AMBIGUO_OU_NEUTRO
