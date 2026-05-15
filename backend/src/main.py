from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from presentation.controllers import (
    proposicao_controller,
    dashboard_controller,
    auth_controller,
)
from infrastructure.database import get_session
from sqlmodel import Session, text
from src import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: executado quando a aplicação inicia
    print("🚀 Iniciando e verificando banco de dados...")
    try:
        init_db.run()
        print("✅ Banco de dados pronto!")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
    yield
    # Shutdown: executado quando a aplicação encerra
    print("👋 Backend Monitor Legislativo encerrado.")


app = FastAPI(title="Monitor Legislativo API", lifespan=lifespan)

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
        # Executa uma consulta simples para validar a conexão com o banco
        session.exec(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "error", "database": "disconnected"}


# Incluindo as rotas da camada de apresentação
app.include_router(auth_controller.router)
app.include_router(proposicao_controller.router)
app.include_router(dashboard_controller.router)
