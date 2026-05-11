from fastapi import FastAPI  # type: ignore

from presentation.controllers.proposicao_controller import router

app = FastAPI(title="Monitor Legislativo API")

app.include_router(router)


@app.get("/")
def root():
    return {"message": "API rodando"}


@app.get("/health")
def health():
    return {"status": "ok"}
