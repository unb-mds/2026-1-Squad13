from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, ConfigDict, Field
from application.services.buscar_proposicoes_service import BuscarProposicoesService
from application.services.detalhe_proposicao_service import DetalheProposicaoService
from infrastructure.repositories.sql_proposicao_repository import SQLProposicaoRepository
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.database import get_session
from sqlmodel import Session

router = APIRouter()

# --- Schemas ---

class ProposicaoResponse(BaseModel):
    """Schema para retorno na API com normalização camelCase"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    tipo: str
    numero: str
    ano: int
    ementa: str
    ementaResumida: Optional[str] = Field(default=None, alias="ementaResumida")
    autor: str
    orgaoOrigem: Optional[str] = Field(default=None, alias="orgaoOrigem")
    status: str
    orgaoAtual: str
    dataApresentacao: str
    dataUltimaMovimentacao: str
    tempoTotalDias: int
    temAtraso: bool
    atrasoCritico: bool = Field(alias="atrasoCritico")
    temPrevisaoIA: bool
    tags: List[str]
    linkOficial: Optional[str] = Field(default=None, alias="linkOficial")
    dataEncerramento: Optional[str] = Field(default=None, alias="dataEncerramento")
    previsaoAprovacaoDias: Optional[int] = Field(default=None, alias="previsaoAprovacaoDias")

class ProposicoesListResponse(BaseModel):
    items: List[ProposicaoResponse]
    total: int
    pagina: int
    totalPaginas: int = Field(alias="totalPaginas")

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
        "orgaoAtual": p.orgao_atual,
        "dataApresentacao": p.data_apresentacao,
        "dataUltimaMovimentacao": p.data_ultima_movimentacao,
        "tempoTotalDias": p.tempo_total_dias or 0,
        "temAtraso": p.tem_atraso or False,
        "atrasoCritico": p.atraso_critico,
        "temPrevisaoIA": p.tem_previsao_ia or False,
        "tags": p.tags or [],
        "linkOficial": p.link_oficial,
        "dataEncerramento": p.data_encerramento,
        "previsaoAprovacaoDias": p.previsao_aprovacao_dias,
    }

# --- Controller ---

@router.get("/proposicoes", response_model=ProposicoesListResponse)
def buscar_proposicoes(
    busca: Optional[str] = Query(default=None),
    tipo: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    orgao_origem: Optional[str] = Query(default=None, alias="orgaoOrigem"),
    data_inicio: Optional[str] = Query(default=None, alias="dataInicio"),
    data_fim: Optional[str] = Query(default=None, alias="dataFim"),
    pagina: int = Query(default=1, ge=1),
    itens_por_pagina: int = Query(default=10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    repository = SQLProposicaoRepository(session)
    service = BuscarProposicoesService(repository)

    filtros = {
        "busca": busca,
        "tipo": tipo,
        "status": status,
        "orgao_origem": orgao_origem,
        "data_inicio": data_inicio,
        "data_fim": data_fim
    }

    try:
        resultado = service.executar(
            filtros=filtros,
            pagina=pagina,
            itens_por_pagina=itens_por_pagina
        )

        return {
            "items": [_to_response(p) for p in resultado["items"]],
            "total": resultado["total"],
            "pagina": resultado["pagina"],
            "totalPaginas": resultado["total_paginas"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/proposicoes/{id}", response_model=ProposicaoResponse)
def obter_detalhe_proposicao(
    id: str,
    session: Session = Depends(get_session)
):
    repository = SQLProposicaoRepository(session)
    camara_adapter = CamaraAdapter()
    senado_adapter = SenadoAdapter()
    service = DetalheProposicaoService(repository, camara_adapter, senado_adapter)

    try:
        proposicao = service.executar(id)
        return _to_response(proposicao)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
