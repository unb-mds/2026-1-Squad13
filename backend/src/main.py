import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, text

from infrastructure.config import settings
from infrastructure.database import close_redis, get_session, init_redis
from presentation.controllers import (
    auth_controller,
    dashboard_controller,
    proposicao_controller,
)

import init_db

# Configuração de Logging Estruturado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: executado quando a aplicação inicia
    logger.info("🚀 Iniciando e verificando banco de dados...")
    try:
        init_db.run()
        logger.info("✅ Banco de dados pronto!")
        # Inicializa pool de conexões Redis
        init_redis()
        logger.info("✅ Redis inicializado!")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar serviços: {e}")
    yield
    # Shutdown: executado quando a aplicação encerra
    close_redis()
    logger.info("👋 Backend Monitor Legislativo encerrado.")


app = FastAPI(title="Monitor Legislativo API", lifespan=lifespan)

# Configuração de CORS via settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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
