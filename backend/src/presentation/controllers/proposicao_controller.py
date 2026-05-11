from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from application.services.buscar_proposicoes_service import BuscarProposicoesService
from infrastructure.repositories.sql_proposicao_repository import SQLProposicaoRepository
from infrastructure.database import get_session
from sqlmodel import Session

router = APIRouter()

# --- Schemas ---

class ProposicaoRead(BaseModel):
    """Schema para retorno na API com normalização camelCase"""
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    tipo: str
    numero: int
    ano: int
    autor: str
    uf_autor: str
    status_tramitacao: str
    ementa: str
    data_apresentacao: str
    data_ultima_movimentacao: str
    orgao_atual: str
    link_oficial: Optional[str]
    tags: List[str]

class PaginatedProposicoes(BaseModel):
    items: List[ProposicaoRead]
    total: int

# --- Controller ---

@router.get("/proposicoes", response_model=PaginatedProposicoes)
def buscar_proposicoes(
    tipo: str | None = Query(default=None),
    numero: int | None = Query(default=None),
    ano: int | None = Query(default=None),
    autor: str | None = Query(default=None),
    uf_autor: str | None = Query(default=None),
    status_tramitacao: str | None = Query(default=None),
    session: Session = Depends(get_session)
):
    # Injeção de dependência via parâmetro do endpoint
    repository = SQLProposicaoRepository(session)
    service = BuscarProposicoesService(repository)
    
    try:
        resultados = service.executar(
            tipo=tipo,
            numero=numero,
            ano=ano,
            autor=autor,
            uf_autor=uf_autor,
            status_tramitacao=status_tramitacao
        )
        return {
            "items": resultados,
            "total": len(resultados)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
