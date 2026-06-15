import logging
import time

import httpx
from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select, text

from infrastructure.database import get_redis_client, get_session
from infrastructure.database.models.auditoria_coleta_model import AuditoriaColetaModel
from infrastructure.repositories.sql_auditoria_coleta_repository import (
    SQLAuditoriaColetaRepository,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])

# --- Schemas ---


class HealthComponentStatus(BaseModel):
    status: str = Field(..., description="ok, error, or degraded")
    details: str = Field(..., description="Mensagem de status ou erro")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Geral: ok, error, or degraded")
    timestamp: float
    components: dict[str, HealthComponentStatus]


# --- Logic ---


async def check_api_connectivity(url: str, timeout: float = 2.0) -> bool:
    """Realiza uma requisição HEAD ou GET rápida para validar conectividade."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.head(url)
            return response.status_code == 200
    except Exception as e:
        logger.warning(f"Falha de conectividade com {url}: {e}")
        return False


@router.get("/health", response_model=HealthResponse)
async def health(response: Response, session: Session = Depends(get_session)):
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
            components["redis"] = HealthComponentStatus(
                status="ok", details="Conectado"
            )
        else:
            raise RuntimeError("Redis PING retornou False")
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
        details="Conectado" if camara_ok else "Falha de conectividade",
    )

    # Senado
    senado_ok = await check_api_connectivity(
        "https://legis.senado.leg.br/dadosabertos/materia/atualizadas"
    )
    components["senado_api"] = HealthComponentStatus(
        status="ok" if senado_ok else "degraded",
        details="Conectado" if senado_ok else "Falha de conectividade",
    )

    # 4. Auditoria de Coleta Batch
    try:
        auditoria_repo = SQLAuditoriaColetaRepository(session)
        ultima_exec = auditoria_repo.obter_ultima_execucao("coleta_diaria")

        if ultima_exec:
            # Busca as últimas 3 execuções para checar se houve falhas consecutivas
            statement = (
                select(AuditoriaColetaModel)
                .where(AuditoriaColetaModel.nome_job == "coleta_diaria")
                .order_by(AuditoriaColetaModel.data_inicio.desc())
                .limit(3)
            )
            recentes = session.exec(statement).all()

            falhas_consecutivas = len(recentes) > 0 and all(
                r.status == "falha" for r in recentes
            )

            comp_status = "ok"
            if falhas_consecutivas:
                comp_status = "error"
                details = f"Alerta: Coletas diárias falhando consecutivamente. Última: {ultima_exec.data_inicio.isoformat()} com status {ultima_exec.status}."
            else:
                details = f"Última execução em {ultima_exec.data_inicio.isoformat()} com status {ultima_exec.status}."
                if ultima_exec.status == "falha":
                    comp_status = "degraded"

            components["coleta_batch"] = HealthComponentStatus(
                status=comp_status, details=details
            )
        else:
            components["coleta_batch"] = HealthComponentStatus(
                status="ok",
                details="Nenhuma execução de coleta registrada ainda.",
            )
    except Exception as e:
        logger.error(f"Erro no Healthcheck (Auditoria Coleta): {e}")
        components["coleta_batch"] = HealthComponentStatus(
            status="error", details=str(e)
        )

    # Determinação do status geral
    overall_status = "ok"
    coleta_batch_status = components.get("coleta_batch", {}).status
    if is_critical_failure:
        overall_status = "error"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif not camara_ok or not senado_ok or coleta_batch_status in ["degraded", "error"]:
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status, timestamp=start_time, components=components
    )
