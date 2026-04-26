from fastapi import FastAPI, HTTPException, Query # type: ignore

app = FastAPI(title="Monitor Legislativo API")

MOCK_PROPOSICOES = [
    {
        "id": 1,
        "tipo": "PL",
        "numero": 123,
        "ano": 2024,
        "autor": "João Silva",
        "uf_autor": "DF",
        "status_tramitacao": "Em tramitação",
        "ementa": "Dispõe sobre transparência em processos públicos."
    },
    {
        "id": 2,
        "tipo": "PEC",
        "numero": 45,
        "ano": 2023,
        "autor": "Maria Souza",
        "uf_autor": "SP",
        "status_tramitacao": "Aprovada",
        "ementa": "Altera dispositivo constitucional sobre orçamento."
    },
]

@app.get("/")
def root():
    return {"message": "API rodando"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/proposicoes")
def buscar_proposicoes(
    tipo: str | None = Query(default=None),
    numero: int | None = Query(default=None),
    ano: int | None = Query(default=None),
    autor: str | None = Query(default=None),
    uf_autor: str | None = Query(default=None),
    status_tramitacao: str | None = Query(default=None),
):
    filtros = [tipo, numero, ano, autor, uf_autor, status_tramitacao]

    if not any(valor is not None and str(valor).strip() != "" for valor in filtros):
        raise HTTPException(
            status_code=400,
            detail="Preencha pelo menos um filtro para realizar a busca."
        )

    resultados = MOCK_PROPOSICOES

    if tipo:
        resultados = [x for x in resultados if x["tipo"].lower() == tipo.lower()]
    if numero:
        resultados = [x for x in resultados if x["numero"] == numero]
    if ano:
        resultados = [x for x in resultados if x["ano"] == ano]
    if autor:
        resultados = [x for x in resultados if autor.lower() in x["autor"].lower()]
    if uf_autor:
        resultados = [x for x in resultados if x["uf_autor"].lower() == uf_autor.lower()]
    if status_tramitacao:
        resultados = [
            x for x in resultados
            if x["status_tramitacao"].lower() == status_tramitacao.lower()
        ]

    return {
        "items": resultados,
        "total": len(resultados)
    }