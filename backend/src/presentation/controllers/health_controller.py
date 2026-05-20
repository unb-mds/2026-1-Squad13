import time
import httpx
import logging
from typing import Dict
from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field
from sqlmodel import Session, text
from infrastructure.database import get_session, get_redis_client
from infrastructure.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])

# --- Schemas ---

class HealthComponentStatus(BaseModel):
    status: str = Field(..., description="ok, error, or degraded")
    details: str = Field(..., description="Mensagem de status ou erro")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Geral: ok, error, or degraded")
    timestamp: float
    components: Dict[str, HealthComponentStatus]

# --- Logic ---

async def check_api_connectivity(url: str, timeout: float = 2.0) -> bool:
    """Realiza uma requisição HEAD ou GET rápida para validar conectividade."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Usamos um endpoint de referências que é leve e estável
            response = await client.get(url)
            return response.status_code == 200
    except Exception as e:
        logger.warning(f"Falha de conectividade com {url}: {e}")
        return False

@router.get("/health", response_model=HealthResponse)
async def health(
    response: Response,
    session: Session = Depends(get_session)
):
    """
    Verifica a saúde das dependências críticas (DB, Redis, APIs Externas).
    Retorna 503 se dependências vitais (DB ou Redis) estiverem offline.
    """
    start_time = time.time()
    components = {}
    is_critical_failure = False
    
    # 1. Banco de Dados (Crítico)
    try:
        session.exec(text("SELECT 1"))
        components["database"] = HealthComponentStatus(status="ok", details="Conectado")
    except Exception as e:
        logger.error(f"Erro no Healthcheck (Database): {e}")
        components["database"] = HealthComponentStatus(status="error", details=str(e))
        is_critical_failure = True

    # 2. Redis (Crítico)
    try:
        redis_client = get_redis_client()
        if redis_client.ping():
            components["redis"] = HealthComponentStatus(status="ok", details="Conectado")
        else:
            raise Exception("Redis PING retornou False")
    except Exception as e:
        logger.error(f"Erro no Healthcheck (Redis): {e}")
        components["redis"] = HealthComponentStatus(status="error", details=str(e))
        is_critical_failure = True

    # 3. APIs Externas (Não-crítico, mas sinaliza degradado)
    # Câmara
    camara_ok = await check_api_connectivity(
        "https://dadosabertos.camara.leg.br/api/v2/referencias/situacoesProposicao"
    )
    components["camara_api"] = HealthComponentStatus(
        status="ok" if camara_ok else "degraded",
        details="Conectado" if camara_ok else "Falha de conectividade"
    )

    # Senado
    senado_ok = await check_api_connectivity(
        "https://www25.senado.leg.br/dadosabertos/materia/tipos"
    )
    components["senado_api"] = HealthComponentStatus(
        status="ok" if senado_ok else "degraded",
        details="Conectado" if senado_ok else "Falha de conectividade"
    )

    # Determinação do status geral
    overall_status = "ok"
    if is_critical_failure:
        overall_status = "error"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif not camara_ok or not senado_ok:
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        timestamp=start_time,
        components=components
    )
