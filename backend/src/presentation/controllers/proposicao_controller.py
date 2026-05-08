from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from typing import List
from application.services.buscar_proposicoes_service import BuscarProposicoesService
from infrastructure.repositories.proposicao_repository import ProposicaoRepository

router = APIRouter()

# --- Schemas (Poderiam estar em um arquivo separado) ---

def to_camel(string: str) -> str:
    """Converte snake_case para camelCase"""
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])

class ProposicaoRead(BaseModel):
    """Schema para retorno na API com normalização camelCase"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
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

# Injeção de dependência manual (simplificada para o MVP)
repository = ProposicaoRepository()
service = BuscarProposicoesService(repository)

@router.get("/proposicoes", response_model=PaginatedProposicoes)
def buscar_proposicoes(
    tipo: str | None = Query(default=None),
    numero: int | None = Query(default=None),
    ano: int | None = Query(default=None),
    autor: str | None = Query(default=None),
    uf_autor: str | None = Query(default=None),
    status_tramitacao: str | None = Query(default=None),
):
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
