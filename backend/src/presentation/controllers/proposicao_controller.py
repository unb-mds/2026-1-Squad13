from fastapi import APIRouter, HTTPException, Query
from application.services.buscar_proposicoes_service import BuscarProposicoesService
from infrastructure.repositories.proposicao_repository import ProposicaoRepository

router = APIRouter()

# Injeção de dependência manual (simplificada para o MVP)
repository = ProposicaoRepository()
service = BuscarProposicoesService(repository)

@router.get("/proposicoes")
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
