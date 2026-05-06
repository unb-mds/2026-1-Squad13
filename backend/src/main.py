from fastapi import FastAPI
from presentation.controllers import proposicao_controller

app = FastAPI(title="Monitor Legislativo API")

@app.get("/")
def root():
    return {"message": "API rodando"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Incluindo as rotas da camada de apresentação
app.include_router(proposicao_controller.router)
