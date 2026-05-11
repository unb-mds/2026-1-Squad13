from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from presentation.controllers import proposicao_controller

app = FastAPI(title="Monitor Legislativo API")

# Configuração de CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API rodando"}


@app.get("/health")
def health():
    return {"status": "ok"}

# Incluindo as rotas da camada de apresentação
app.include_router(proposicao_controller.router)
