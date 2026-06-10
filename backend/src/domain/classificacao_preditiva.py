"""
Módulo de Domínio para classificação preditiva de proposições.
Contém lógicas de negócio puras que não dependem de I/O ou frameworks.
"""


def classificar_tema_economico(ementa: str | None) -> bool:
    """
    Classifica se uma proposição possui tema econômico baseado em palavras-chave na ementa.
    """
    if not ementa:
        return False

    ementa_lower = ementa.lower()
    palavras_chave = [
        "tributo",
        "tributário",
        "tributária",
        "tributario",
        "tributaria",
        "imposto",
        "taxa",
        "contribuição",
        "contribuições",
        "contribuicao",
        "contribuicoes",
        "orçamento",
        "orçamentário",
        "orçamentária",
        "orcamento",
        "orcamentario",
        "orcamentaria",
        "fiscal",
        "financeiro",
        "financeira",
        "finanças",
        "financas",
        "crédito",
        "credito",
        "despesa",
        "receita",
        "economia",
        "econômico",
        "econômica",
        "economico",
        "economica",
        "ldo",
        "loa",
        "ppa",
        "pis",
        "cofins",
        "icms",
        "ipi",
        "iptu",
        "ipva",
        "irf",
        "iss",
    ]

    # Busca por palavras inteiras para evitar falsos positivos (ex: "receita" dentro de "engenheiro")
    # Substitui caracteres de pontuação e hífens por espaços para isolar as palavras
    ementa_limpa = ementa_lower
    for char in ".,;:-()[]{}":
        ementa_limpa = ementa_limpa.replace(char, " ")
        
    palavras_ementa = set(ementa_limpa.split())
    
    return any(k in palavras_ementa for k in palavras_chave)


def identificar_autor_executivo(autor_nome: str | None) -> bool:
    """
    Identifica se o autor da proposição pertence ao Poder Executivo.
    """
    if not autor_nome:
        return False

    autor_lower = autor_nome.lower()
    return "poder executivo" in autor_lower or "presidente" in autor_lower
