from typing import Optional

from fastapi import APIRouter, Query  # type: ignore
from pydantic import BaseModel  # type: ignore

from application.services.buscar_proposicoes_service import BuscarProposicoesService
from infrastructure.adapters.camara_mock_adapter import CamaraMockAdapter
from infrastructure.adapters.senado_mock_adapter import SenadoMockAdapter

router = APIRouter()

_service = BuscarProposicoesService([CamaraMockAdapter(), SenadoMockAdapter()])


class ProposicaoResponse(BaseModel):
    id: str
    tipo: str
    numero: str
    ano: int
    ementa: str
    ementaResumida: str
    autor: str
    orgaoOrigem: str
    status: str
    orgaoAtual: str
    dataApresentacao: str
    dataUltimaMovimentacao: str
    tempoTotalDias: int
    temAtraso: bool
    temPrevisaoIA: bool
    tags: list[str]
    linkOficial: Optional[str] = None
    dataEncerramento: Optional[str] = None
    previsaoAprovacaoDias: Optional[int] = None


class ProposicoesListResponse(BaseModel):
    items: list[ProposicaoResponse]
    total: int
    pagina: int
    totalPaginas: int


def _to_response(p) -> dict:
    return {
        "id": p.id,
        "tipo": p.tipo,
        "numero": p.numero,
        "ano": p.ano,
        "ementa": p.ementa,
        "ementaResumida": p.ementa_resumida,
        "autor": p.autor,
        "orgaoOrigem": p.orgao_origem,
        "status": p.status,
        "orgaoAtual": p.orgao_atual,
        "dataApresentacao": p.data_apresentacao,
        "dataUltimaMovimentacao": p.data_ultima_movimentacao,
        "tempoTotalDias": p.tempo_total_dias,
        "temAtraso": p.tem_atraso,
        "temPrevisaoIA": p.tem_previsao_ia,
        "tags": p.tags,
        "linkOficial": p.link_oficial,
        "dataEncerramento": p.data_encerramento,
        "previsaoAprovacaoDias": p.previsao_aprovacao_dias,
    }


@router.get("/proposicoes", response_model=ProposicoesListResponse)
def buscar_proposicoes(
    busca: str = Query(default=""),
    tipo: str = Query(default=""),
    status: str = Query(default=""),
    orgaoOrigem: str = Query(default=""),
    dataInicio: str = Query(default=""),
    dataFim: str = Query(default=""),
    pagina: int = Query(default=1, ge=1),
    itensPorPagina: int = Query(default=10, ge=1, le=100),
):
    filtros = {
        "busca": busca,
        "tipo": tipo,
        "status": status,
        "orgao_origem": orgaoOrigem,
        "data_inicio": dataInicio,
        "data_fim": dataFim,
    }
    resultado = _service.executar(filtros, pagina, itensPorPagina)

    return {
        "items": [_to_response(p) for p in resultado["items"]],
        "total": resultado["total"],
        "pagina": resultado["pagina"],
        "totalPaginas": resultado["total_paginas"],
    }
