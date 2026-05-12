from fastapi import APIRouter, Depends
from pydantic import BaseModel
from application.services.dashboard_service import DashboardService
from infrastructure.repositories.sql_proposicao_repository import SQLProposicaoRepository
from infrastructure.database import get_session
from sqlmodel import Session

router = APIRouter()

class DashboardMetricasResponse(BaseModel):
    tempoMedioTramitacao: int
    totalProposicoes: int
    proposicoesComAtraso: int
    totalAprovadas: int
    totalEmTramitacao: int
    totalRejeitadas: int
    comissaoMaiorTempo: str
    comissaoMaiorTempoMedia: int

@router.get("/dashboard/metricas", response_model=DashboardMetricasResponse)
def obter_metricas(session: Session = Depends(get_session)):
    repository = SQLProposicaoRepository(session)
    service = DashboardService(repository)
    return service.obter_metricas()
