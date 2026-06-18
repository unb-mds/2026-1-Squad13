from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from application.services.atualizar_cobertura_service import AtualizarCoberturaService
from application.services.dashboard_service import DashboardService
from presentation.dashboard_dependencies import (
    get_atualizar_cobertura_service,
    get_dashboard_service,
)

router = APIRouter(tags=["Dashboard"])


class TrendInfoResponse(BaseModel):
    value: str
    isPositive: bool = Field(alias="isPositive")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }


class DashboardMetricasResponse(BaseModel):
    tempoMedioTramitacao: int
    totalProposicoes: int
    proposicoesComAtraso: int
    totalAprovadas: int
    totalEmTramitacao: int
    totalRejeitadas: int
    comissaoMaiorTempo: str
    comissaoMaiorTempoMedia: int
    iarMedio: float
    ieiMedio: float
    percentualAtrasadas: int
    totalProposicoesTrend: TrendInfoResponse | None = Field(
        default=None, alias="totalProposicoesTrend"
    )
    totalEmTramitacaoTrend: TrendInfoResponse | None = Field(
        default=None, alias="totalEmTramitacaoTrend"
    )
    proposicoesComAtrasoTrend: TrendInfoResponse | None = Field(
        default=None, alias="proposicoesComAtrasoTrend"
    )
    tempoMedioTramitacaoTrend: TrendInfoResponse | None = Field(
        default=None, alias="tempoMedioTramitacaoTrend"
    )

    model_config = {
        "populate_by_name": True,
    }


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


class EvolucaoTemporalResponse(BaseModel):
    mes: str
    entradas: int
    saidas: int


class TransicaoItemResponse(BaseModel):
    origem: str
    destino: str
    quantidade: int
    tempoMedioTransicao: int = Field(alias="tempoMedioTransicao")


class TransicoesCasasResponse(BaseModel):
    transitions: list[TransicaoItemResponse]
    totalCamara: int = Field(alias="totalCamara")
    totalSenado: int = Field(alias="totalSenado")


class EstoqueFaseItem(BaseModel):
    codigo: str
    nome: str
    natureza: str
    permiteEstoqueAtual: bool = Field(validation_alias="permite_estoque_atual")
    total: int

    model_config = {
        "populate_by_name": True,
    }


class DashboardEstoqueResponse(BaseModel):
    ativo: list[EstoqueFaseItem]
    passivo: list[EstoqueFaseItem]


class DashboardHandoffResponse(BaseModel):
    totalEmTransito: int = Field(validation_alias="total_em_transito")
    medianaDiasTransito: int = Field(validation_alias="mediana_dias_transito")

    model_config = {
        "populate_by_name": True,
    }


class CoberturaMetricaResponse(BaseModel):
    ano: int
    tipoProposicao: str = Field(validation_alias="tipo_proposicao")
    fonte: str = Field(default="")  # "camara" | "senado"
    totalLocal: int = Field(validation_alias="total_local")
    totalApiOficial: int = Field(validation_alias="total_api_oficial")
    percentualCobertura: float = Field(validation_alias="percentual_cobertura")
    dataAtualizacao: datetime | None = Field(validation_alias="data_atualizacao")

    model_config = {
        "populate_by_name": True,
    }


class DashboardQualidadeResponse(BaseModel):
    completudePorcentagem: float = Field(validation_alias="completude_porcentagem")
    totalProposicoes: int = Field(validation_alias="total_proposicoes")
    camposAnalisados: int = Field(validation_alias="campos_analisados")

    model_config = {
        "populate_by_name": True,
    }


class DashboardFilterParams(BaseModel):
    busca: str | None = Field(default=None)
    tipo: str | None = Field(default=None)
    status: str | None = Field(default=None)
    orgao_origem: str | None = Field(default=None, alias="orgaoOrigem")
    data_inicio: str | None = Field(default=None, alias="dataInicio")
    data_fim: str | None = Field(default=None, alias="dataFim")
    rito: str | None = Field(default=None)

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


@router.get("/dashboard/grafico-tipo", response_model=list[DadosGraficoTipoResponse])
def obter_dados_tipo(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_dados_tipo(filtros_dict or None)


@router.get(
    "/dashboard/grafico-comissao", response_model=list[DadosGraficoComissaoResponse]
)
def obter_dados_comissao(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_dados_comissao(filtros_dict or None)


@router.get(
    "/dashboard/grafico-status", response_model=list[DadosGraficoStatusResponse]
)
def obter_dados_status(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_dados_status(filtros_dict or None)


@router.get("/dashboard/gargalos", response_model=list[GargaloInstitucionalResponse])
def obter_gargalos(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_gargalos(filtros_dict or None)


@router.get("/dashboard/comparacao-temas", response_model=list[ComparacaoTemaResponse])
def obter_comparacao_temas(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_comparacao_temas(filtros_dict or None)


@router.get("/dashboard/tempo-por-fase", response_model=list[TempoPorFaseResponse])
def obter_tempo_por_fase(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_tempo_por_fase(filtros_dict or None)


@router.get(
    "/dashboard/evolucao-temporal",
    response_model=list[EvolucaoTemporalResponse],
)
def obter_evolucao_temporal(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_evolucao_temporal(filtros_dict or None)


@router.get("/dashboard/transicoes-casas", response_model=TransicoesCasasResponse)
def obter_transicoes_casas(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_transicoes_casas(filtros_dict or None)


@router.get("/dashboard/estoque", response_model=DashboardEstoqueResponse)
def obter_estoque(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    dados = service.obter_estoque_fases(filtros_dict or None)
    ativo = [
        item
        for item in dados
        if item["natureza"] == "operacional" and item["permite_estoque_atual"]
    ]
    passivo = [item for item in dados if item["natureza"] == "terminal"]
    return {"ativo": ativo, "passivo": passivo}


@router.get("/dashboard/handoff", response_model=DashboardHandoffResponse)
def obter_handoff(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_mediana_handoff(filtros_dict or None)


@router.get("/dashboard/cobertura", response_model=list[CoberturaMetricaResponse])
def obter_cobertura(
    filtros: DashboardFilterParams = Depends(),
    cobertura_service: AtualizarCoberturaService = Depends(
        get_atualizar_cobertura_service
    ),
):
    filtros_dict = _montar_filtros(filtros)
    return cobertura_service.obter_todas_metricas_cobertura(filtros_dict or None)


@router.get("/dashboard/qualidade", response_model=DashboardQualidadeResponse)
def obter_qualidade(
    filtros: DashboardFilterParams = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    filtros_dict = _montar_filtros(filtros)
    return service.obter_qualidade_base(filtros_dict or None)
