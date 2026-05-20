from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from application.services.dashboard_service import DashboardService
from infrastructure.cache.redis_client import RedisClient
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)
from infrastructure.database import get_session, get_redis_client
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
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


class TempoPorFaseResponse(BaseModel):
    fase: str
    codigoFase: str
    ordemLogica: int
    tempoMedioDias: int
    quantidadeProposicoes: int


def get_dashboard_service(session: Session = Depends(get_session)) -> DashboardService:
    repository = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    fase_repo = SQLFaseAnaliticaRepository(session)
    redis_conn = get_redis_client()
    cache_provider = RedisClient(redis_conn)
    return DashboardService(
        repository, evento_repo, fase_repo=fase_repo, cache_provider=cache_provider
    )


class DashboardFilterParams(BaseModel):
    busca: Optional[str] = Field(default=None)
    tipo: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    orgao_origem: Optional[str] = Field(default=None, alias="orgaoOrigem")
    data_inicio: Optional[str] = Field(default=None, alias="dataInicio")
    data_fim: Optional[str] = Field(default=None, alias="dataFim")

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True, by_alias=False)

def _montar_filtros(params: DashboardFilterParams) -> dict:
    return params.to_dict()


@router.get("/dashboard/metricas", response_model=DashboardMetricasResponse)
def obter_metricas(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_metricas(filtros_dict or None)


@router.get("/dashboard/grafico-tipo", response_model=List[DadosGraficoTipoResponse])
def obter_dados_tipo(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_dados_tipo(filtros_dict or None)


@router.get(
    "/dashboard/grafico-comissao", response_model=List[DadosGraficoComissaoResponse]
)
def obter_dados_comissao(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_dados_comissao(filtros_dict or None)


@router.get(
    "/dashboard/grafico-status", response_model=List[DadosGraficoStatusResponse]
)
def obter_dados_status(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_dados_status(filtros_dict or None)


@router.get("/dashboard/gargalos", response_model=List[GargaloInstitucionalResponse])
def obter_gargalos(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_gargalos(filtros_dict or None)


@router.get("/dashboard/comparacao-temas", response_model=List[ComparacaoTemaResponse])
def obter_comparacao_temas(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_comparacao_temas(filtros_dict or None)


@router.get("/dashboard/tempo-por-fase", response_model=List[TempoPorFaseResponse])
def obter_tempo_por_fase(service: DashboardService = Depends(get_dashboard_service)):
    return service.obter_tempo_por_fase()
