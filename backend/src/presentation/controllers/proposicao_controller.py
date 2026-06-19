from enum import StrEnum

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from application.services.buscar_proposicoes_service import BuscarProposicoesService
from application.services.detalhe_proposicao_service import DetalheProposicaoService
from application.services.gerar_estimativa_service import GerarEstimativaUseCase
from application.services.listar_movimentacoes_service import ListarMovimentacoesService
from application.services.obter_confiabilidade_service import ObterConfiabilidadeService
from domain.value_objects.modo_movimentacao import ModoMovimentacao
from presentation.proposicao_dependencies import (
    get_buscar_proposicoes_service,
    get_detalhe_proposicao_service,
    get_gerar_estimativa_use_case,
    get_listar_movimentacoes_service,
    get_obter_confiabilidade_service,
)
from domain.entities.evento_tramitacao import calcular_tempo_por_fase

router = APIRouter(tags=["Proposições"])

# --- Schemas ---


class BreakdownFase(BaseModel):
    fase: str
    dias: int


class EventoTramitacaoResponse(BaseModel):
    """Schema para retorno de eventos de tramitação com normalização camelCase"""

    model_config = ConfigDict(from_attributes=True)

    proposicaoId: str = Field(alias="proposicaoId")
    dataEvento: str = Field(alias="dataEvento")
    sequencia: int
    siglaOrgao: str | None = Field(default=None, alias="siglaOrgao")
    descricaoOriginal: str = Field(alias="descricaoOriginal")
    tipoEvento: str = Field(alias="tipoEvento")
    faseAnaliticaId: int | None = Field(default=None, alias="faseAnaliticaId")
    deliberativo: bool
    mudouFase: bool = Field(alias="mudouFase")
    mudouOrgao: bool = Field(alias="mudouOrgao")
    remessaOuRetorno: str | None = Field(default=None, alias="remessaOuRetorno")
    diasNaEtapa: int = Field(alias="diasNaEtapa")
    temAtraso: bool = Field(alias="temAtraso")
    relevante: bool


class ProposicaoResponse(BaseModel):
    """Schema para retorno na API com normalização camelCase"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    tipo: str
    numero: str
    ano: int
    ementa: str
    ementaResumida: str | None = Field(default=None, alias="ementaResumida")
    autor: str
    orgaoOrigem: str | None = Field(default=None, alias="orgaoOrigem")
    status: str
    statusOriginal: str | None = Field(default=None, alias="statusOriginal")
    orgaoAtual: str
    dataApresentacao: str
    dataUltimaMovimentacao: str
    tempoTotalDias: int
    temAtraso: bool
    atrasoCritico: bool = Field(alias="atrasoCritico")
    temPrevisaoIA: bool
    tags: list[str]
    linkOficial: str | None = Field(default=None, alias="linkOficial")
    codigoNormalizado: str | None = Field(default=None, alias="codigoNormalizado")
    dataEncerramento: str | None = Field(default=None, alias="dataEncerramento")
    previsaoAprovacaoDias: int | None = Field(
        default=None, alias="previsaoAprovacaoDias"
    )
    indiceAtrasoRelativo: float | None = Field(
        default=None, alias="indiceAtrasoRelativo"
    )
    indiceAtrasoFaseAtual: float | None = Field(
        default=None, alias="indiceAtrasoFaseAtual"
    )
    indiceEsperaImprodutiva: float | None = Field(
        default=None, alias="indiceEsperaImprodutiva"
    )
    statusAtraso: str | None = Field(default=None, alias="statusAtraso")
    diasDecorridosTotal: int | None = Field(default=None, alias="diasDecorridosTotal")
    diasEsperadosTotal: int | None = Field(default=None, alias="diasEsperadosTotal")
    baselineGrupoId: str | None = Field(default=None, alias="baselineGrupoId")
    dataCalculoMetricas: str | None = Field(default=None, alias="dataCalculoMetricas")
    regimeTramitacao: str | None = Field(default=None, alias="regimeTramitacao")
    coberturaDados: int = Field(alias="coberturaDados")
    confiabilidade: str = Field(alias="confiabilidade")
    tempoPorFase: list[BreakdownFase] | None = Field(default=None, alias="tempoPorFase")


class ProposicoesListResponse(BaseModel):
    items: list[ProposicaoResponse]
    total: int
    pagina: int
    totalPaginas: int = Field(alias="totalPaginas")


class StatusEstimativa(StrEnum):
    CALCULADA = "CALCULADA"
    DADOS_INSUFICIENTES = "DADOS_INSUFICIENTES"


class ConfiabilidadeResponse(BaseModel):
    cobertura: int
    statusHistorico: str = Field(alias="statusHistorico")
    ultimaAtualizacao: str = Field(alias="ultimaAtualizacao")
    fontes: list[str]
    limitacoes: list[str]
    confiabilidade: str


class EventoResumoResponse(BaseModel):
    eventoId: int | None = Field(default=None, alias="eventoId")
    tipoEvento: str = Field(alias="tipoEvento")
    descricaoOriginal: str = Field(alias="descricaoOriginal")
    dataEvento: str = Field(alias="dataEvento")
    siglaOrgao: str | None = Field(default=None, alias="siglaOrgao")
    deliberativo: bool
    diasNaEtapa: int | None = Field(default=None, alias="diasNaEtapa")
    marcaApensacao: bool = Field(alias="marcaApensacao")


class PeriodoFaseResponse(BaseModel):
    faseCodigo: str = Field(alias="faseCodigo")
    faseNome: str = Field(alias="faseNome")
    ordemLogica: int = Field(alias="ordemLogica")
    ocorrencia: int
    dataEntrada: str = Field(alias="dataEntrada")
    dataSaida: str | None = Field(default=None, alias="dataSaida")
    diasCorridos: int = Field(alias="diasCorridos")
    eventosRelevantes: list[EventoResumoResponse] = Field(alias="eventosRelevantes")
    motivoTravamento: str | None = Field(default=None, alias="motivoTravamento")
    numeroTurno: int | None = Field(default=None, alias="numeroTurno")
    subtipoFase: str | None = Field(default=None, alias="subtipoFase")


class EstimativaAprovacaoResponse(BaseModel):
    """Schema para retorno da estimativa de aprovação"""

    previsaoAprovacaoDias: int | None = Field(
        default=None,
        alias="previsaoAprovacaoDias",
        description="Estimativa em dias. null se insuficiente.",
    )
    status: StatusEstimativa = Field(..., description="Status do cálculo")
    amostraUtilizada: int = Field(
        alias="amostraUtilizada", description="Tamanho da amostra"
    )


# --- Helper to map snake_case to camelCase for response ---
def _to_response(p) -> dict:
    return {
        "id": str(p.id),
        "tipo": p.tipo,
        "numero": str(p.numero),
        "ano": p.ano,
        "ementa": p.ementa,
        "ementaResumida": p.ementa_resumida,
        "autor": p.autor,
        "orgaoOrigem": p.orgao_origem,
        "status": p.status,
        "statusOriginal": p.status_original,
        "orgaoAtual": p.orgao_atual,
        "dataApresentacao": p.data_apresentacao,
        "dataUltimaMovimentacao": p.data_ultima_movimentacao,
        "tempoTotalDias": p.tempo_total_dias or 0,
        "temAtraso": p.tem_atraso or False,
        "atrasoCritico": p.atraso_critico,
        "temPrevisaoIA": p.tem_previsao_ia or False,
        "tags": p.tags or [],
        "linkOficial": p.link_oficial,
        "codigoNormalizado": p.codigo_normalizado,
        "dataEncerramento": p.data_encerramento,
        "previsaoAprovacaoDias": p.previsao_aprovacao_dias,
        "indiceAtrasoRelativo": p.indice_atraso_relativo,
        "indiceAtrasoFaseAtual": p.indice_atraso_fase_atual,
        "indiceEsperaImprodutiva": p.indice_espera_improdutiva,
        "statusAtraso": p.status_atraso,
        "diasDecorridosTotal": p.dias_decorridos_total,
        "diasEsperadosTotal": p.dias_esperados_total,
        "baselineGrupoId": p.baseline_grupo_id,
        "dataCalculoMetricas": p.data_calculo_metricas.isoformat()
        if p.data_calculo_metricas
        else None,
        "regimeTramitacao": p.regime_tramitacao,
        "coberturaDados": p.cobertura_dados,
        "confiabilidade": p.confiabilidade,
        "tempoPorFase": getattr(p, "tempo_por_fase", None),
    }


def _to_evento_response(e) -> dict:
    data_str = e.data_evento or ""
    if data_str:
        data_str = data_str.replace(" ", "T")
        if not data_str.endswith("Z") and "+" not in data_str:
            data_str += "Z"

    return {
        "proposicaoId": e.proposicao_id,
        "dataEvento": data_str,
        "sequencia": e.sequencia,
        "siglaOrgao": e.sigla_orgao,
        "descricaoOriginal": e.descricao_original,
        "tipoEvento": e.tipo_evento,
        "faseAnaliticaId": e.fase_analitica_id,
        "deliberativo": e.deliberativo,
        "mudouFase": e.mudou_fase,
        "mudouOrgao": e.mudou_orgao,
        "remessaOuRetorno": e.remessa_ou_retorno,
        "diasNaEtapa": e.dias_na_etapa,
        "temAtraso": e.tem_atraso,
        "relevante": getattr(e, "relevante", False),
    }


def _to_periodo_response(p) -> dict:
    return {
        "faseCodigo": p.fase_codigo,
        "faseNome": p.fase_nome,
        "ordemLogica": p.ordem_logica,
        "ocorrencia": p.ocorrencia,
        "dataEntrada": p.data_entrada.isoformat(),
        "dataSaida": p.data_saida.isoformat() if p.data_saida else None,
        "diasCorridos": p.dias_corridos,
        "motivoTravamento": p.motivo_travamento,
        "numeroTurno": p.numero_turno,
        "subtipoFase": p.subtipo_fase,
        "eventosRelevantes": [
            {
                "eventoId": e.evento_id,
                "tipoEvento": e.tipo_evento,
                "descricaoOriginal": e.descricao_original,
                "dataEvento": e.data_evento.replace(" ", "T"),
                "siglaOrgao": e.sigla_orgao,
                "deliberativo": e.deliberativo,
                "diasNaEtapa": e.dias_na_etapa,
                "marcaApensacao": e.marca_apensacao,
            }
            for e in p.eventos_relevantes
        ],
    }


# --- Controller ---


@router.get(
    "/proposicoes/{id}/movimentacoes",
    response_model=list[dict],
)
async def listar_movimentacoes(
    id: str,
    modo: ModoMovimentacao = Query(default=ModoMovimentacao.RESUMIDO),
    service: ListarMovimentacoesService = Depends(get_listar_movimentacoes_service),
):
    try:
        resultado = await service.executar(id, modo=modo)

        if modo == ModoMovimentacao.RESUMIDO:
            return [_to_periodo_response(p) for p in resultado]
        else:
            return [_to_evento_response(e) for e in resultado]
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar movimentações: {str(e)}"
        ) from e


@router.get("/proposicoes", response_model=ProposicoesListResponse)
def buscar_proposicoes(
    busca: str | None = Query(default=None),
    tipo: str | None = Query(default=None),
    status: str | None = Query(default=None),
    orgao_origem: str | None = Query(default=None, alias="orgaoOrigem"),
    data_inicio: str | None = Query(default=None, alias="dataInicio"),
    data_fim: str | None = Query(default=None, alias="dataFim"),
    pagina: int = Query(default=1, ge=1),
    itens_por_pagina: int = Query(default=10, ge=1, le=100),
    service: BuscarProposicoesService = Depends(get_buscar_proposicoes_service),
):
    filtros = {
        "busca": busca,
        "tipo": tipo,
        "status": status,
        "orgao_origem": orgao_origem,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
    }

    try:
        resultado = service.executar(
            filtros=filtros, pagina=pagina, itens_por_pagina=itens_por_pagina
        )

        return {
            "items": [_to_response(p) for p in resultado["items"]],
            "total": resultado["total"],
            "pagina": resultado["pagina"],
            "totalPaginas": resultado["total_paginas"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/proposicoes/{id}", response_model=ProposicaoResponse)
async def obter_detalhe_proposicao(
    id: str, 
    service: DetalheProposicaoService = Depends(get_detalhe_proposicao_service),
    movimentacoes_service: ListarMovimentacoesService = Depends(get_listar_movimentacoes_service),
):
    try:
        proposicao = await service.executar(id)
        
        try:
            eventos = await movimentacoes_service.executar(id, modo=ModoMovimentacao.COMPLETO)
            proposicao.tempo_por_fase = calcular_tempo_por_fase(eventos)
        except Exception as e:
            import logging
            logging.error(f"Erro ao calcular tempo por fase: {e}")
            proposicao.tempo_por_fase = None
            
        return _to_response(proposicao)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}") from e


@router.get(
    "/proposicoes/estimativa/{tipo}/{tema}", response_model=EstimativaAprovacaoResponse
)
def obter_estimativa_aprovacao(
    tipo: str,
    tema: str,
    use_case: GerarEstimativaUseCase = Depends(get_gerar_estimativa_use_case),
):
    """
    Retorna a estimativa de tempo de aprovação para um tipo e tema específicos.
    A lógica de negócio e o threshold de 50 registros estão isolados no Domínio.
    """
    try:
        resultado = use_case.executar(tipo, tema)

        return {
            "previsaoAprovacaoDias": resultado.dias,
            "status": StatusEstimativa(resultado.status),
            "amostraUtilizada": resultado.amostra,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao calcular estimativa: {str(e)}"
        ) from e


@router.get("/proposicoes/{id}/confiabilidade", response_model=ConfiabilidadeResponse)
async def obter_confiabilidade_proposicao(
    id: str,
    service: ObterConfiabilidadeService = Depends(get_obter_confiabilidade_service),
):
    """
    Retorna metadados detalhados de confiabilidade, cobertura, fontes e limitações
    para uma proposição legislativa.
    """
    try:
        return await service.executar(id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}") from e
