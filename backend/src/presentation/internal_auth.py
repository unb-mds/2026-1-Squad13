import secrets

from fastapi import Header, HTTPException, status

from infrastructure.config import settings


async def verify_internal_token(x_internal_token: str = Header(...)):
    if not settings.INTERNAL_API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="INTERNAL_API_SECRET não configurado no servidor.",
        )
    if not secrets.compare_digest(x_internal_token, settings.INTERNAL_API_SECRET):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido."
        )
