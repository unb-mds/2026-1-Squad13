from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from application.services.dashboard_service import DashboardService
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)
from infrastructure.database import get_session
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
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


class DadosGraficoTipoResponse(BaseModel):
    tipo: str
    tempoMedio: int
    quantidade: int


class DadosGraficoComissaoResponse(BaseModel):
    comissao: str
    tempoMedio: int
    quantidade: int


class DadosGraficoStatusResponse(BaseModel):
    status: str
    quantidade: int
    percentual: int


class GargaloInstitucionalResponse(BaseModel):
    orgao: str
    tempoMedioMeses: float
    quantidadeProposicoes: int
    taxaAtraso: int


class ComparacaoTemaResponse(BaseModel):
    tema: str
    tempoMedioDias: int
    taxaAprovacao: int
    velocidade: str



def get_dashboard_service(session: Session = Depends(get_session)) -> DashboardService:
    repository = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    return DashboardService(repository, evento_repo)


def _montar_filtros(
    busca: Optional[str],
    tipo: Optional[str],
    status: Optional[str],
    orgao_origem: Optional[str],
    data_inicio: Optional[str],
    data_fim: Optional[str],
) -> dict:
    filtros = {}
    if busca:
        filtros["busca"] = busca
    if tipo:
        filtros["tipo"] = tipo
    if status:
        filtros["status"] = status
    if orgao_origem:
        filtros["orgao_origem"] = orgao_origem
    if data_inicio:
        filtros["data_inicio"] = data_inicio
    if data_fim:
        filtros["data_fim"] = data_fim
    return filtros


@router.get("/dashboard/metricas", response_model=DashboardMetricasResponse)
def obter_metricas(
    busca: Optional[str] = Query(default=None),
    tipo: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    orgao_origem: Optional[str] = Query(default=None, alias="orgaoOrigem"),
    data_inicio: Optional[str] = Query(default=None, alias="dataInicio"),
    data_fim: Optional[str] = Query(default=None, alias="dataFim"),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros = _montar_filtros(busca, tipo, status, orgao_origem, data_inicio, data_fim)
    return service.obter_metricas(filtros or None)


@router.get("/dashboard/grafico-tipo", response_model=List[DadosGraficoTipoResponse])
def obter_dados_tipo(
    busca: Optional[str] = Query(default=None),
    tipo: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    orgao_origem: Optional[str] = Query(default=None, alias="orgaoOrigem"),
    data_inicio: Optional[str] = Query(default=None, alias="dataInicio"),
    data_fim: Optional[str] = Query(default=None, alias="dataFim"),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros = _montar_filtros(busca, tipo, status, orgao_origem, data_inicio, data_fim)
    return service.obter_dados_tipo(filtros or None)


@router.get(
    "/dashboard/grafico-comissao", response_model=List[DadosGraficoComissaoResponse]
)
def obter_dados_comissao(
    busca: Optional[str] = Query(default=None),
    tipo: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    orgao_origem: Optional[str] = Query(default=None, alias="orgaoOrigem"),
    data_inicio: Optional[str] = Query(default=None, alias="dataInicio"),
    data_fim: Optional[str] = Query(default=None, alias="dataFim"),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros = _montar_filtros(busca, tipo, status, orgao_origem, data_inicio, data_fim)
    return service.obter_dados_comissao(filtros or None)


@router.get(
    "/dashboard/grafico-status", response_model=List[DadosGraficoStatusResponse]
)
def obter_dados_status(
    busca: Optional[str] = Query(default=None),
    tipo: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    orgao_origem: Optional[str] = Query(default=None, alias="orgaoOrigem"),
    data_inicio: Optional[str] = Query(default=None, alias="dataInicio"),
    data_fim: Optional[str] = Query(default=None, alias="dataFim"),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros = _montar_filtros(busca, tipo, status, orgao_origem, data_inicio, data_fim)
    return service.obter_dados_status(filtros or None)


@router.get("/dashboard/gargalos", response_model=List[GargaloInstitucionalResponse])
def obter_gargalos(
    busca: Optional[str] = Query(default=None),
    tipo: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    orgao_origem: Optional[str] = Query(default=None, alias="orgaoOrigem"),
    data_inicio: Optional[str] = Query(default=None, alias="dataInicio"),
    data_fim: Optional[str] = Query(default=None, alias="dataFim"),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros = _montar_filtros(busca, tipo, status, orgao_origem, data_inicio, data_fim)
    return service.obter_gargalos(filtros or None)


@router.get("/dashboard/comparacao-temas", response_model=List[ComparacaoTemaResponse])
def obter_comparacao_temas(
    busca: Optional[str] = Query(default=None),
    tipo: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    orgao_origem: Optional[str] = Query(default=None, alias="orgaoOrigem"),
    data_inicio: Optional[str] = Query(default=None, alias="dataInicio"),
    data_fim: Optional[str] = Query(default=None, alias="dataFim"),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros = _montar_filtros(busca, tipo, status, orgao_origem, data_inicio, data_fim)
    return service.obter_comparacao_temas(filtros or None)
