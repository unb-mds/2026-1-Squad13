import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.config import settings
from infrastructure.database import close_redis, init_redis
from presentation.controllers import (
    dashboard_controller,
    health_controller,
    internal_tasks_controller,
    proposicao_controller,
)
from src import init_db

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
        init_db.run_sem_integridade()
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


# Incluindo as rotas da camada de apresentação
app.include_router(proposicao_controller.router)
app.include_router(dashboard_controller.router)
app.include_router(health_controller.router)
app.include_router(internal_tasks_controller.router)
