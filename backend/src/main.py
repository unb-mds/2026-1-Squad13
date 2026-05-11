from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from presentation.controllers import proposicao_controller
from infrastructure.database import get_session
from sqlmodel import Session, text

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
def health(session: Session = Depends(get_session)):
    try:
        # Tenta executar uma consulta simples no banco
        session.exec(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}, 503

# Incluindo as rotas da camada de apresentação
app.include_router(proposicao_controller.router)
