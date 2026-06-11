import logging
import uuid
from typing import Optional

import redis

from application.ports.password_reset_token_provider import PasswordResetTokenProvider

logger = logging.getLogger(__name__)


class RedisPasswordResetTokenProvider(PasswordResetTokenProvider):
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.prefix_email_to_token = "pwd_reset_email:"
        self.prefix_token_to_email = "pwd_reset_token:"
        self.ttl_seconds = 3600  # 1 hora

    def gerar_token(self, email: str) -> str:
        """Gera um token de uso único com TTL de 1 hora para o e-mail informado.
        Ao gerar um novo token, o anterior deve ser invalidado."""
        novo_token = str(uuid.uuid4())
        chave_email = f"{self.prefix_email_to_token}{email}"

        try:
            # Invalida token anterior se existir
            token_antigo = self.redis_client.get(chave_email)
            if token_antigo:
                # Se o cliente já usa decode_responses=True, token_antigo já é str
                if isinstance(token_antigo, bytes):
                    token_antigo = token_antigo.decode("utf-8")

                chave_token_antigo = f"{self.prefix_token_to_email}{token_antigo}"
                self.redis_client.delete(chave_token_antigo)

            # Salva o novo token
            chave_novo_token = f"{self.prefix_token_to_email}{novo_token}"
            self.redis_client.setex(chave_novo_token, self.ttl_seconds, email)

            # Atualiza o mapeamento de email para o token atual
            self.redis_client.setex(chave_email, self.ttl_seconds, novo_token)

            return novo_token
        except redis.RedisError as e:
            logger.error(
                f"Erro ao gerar token de recuperação no Redis para {email}: {e}"
            )
            raise

    def validar_token(self, token: str) -> Optional[str]:
        """Valida o token e retorna o e-mail associado, ou None se inválido/expirado."""
        chave_token = f"{self.prefix_token_to_email}{token}"
        try:
            email = self.redis_client.get(chave_token)
            if email:
                if isinstance(email, bytes):
                    return email.decode("utf-8")
                return email
            return None
        except redis.RedisError as e:
            logger.error(f"Erro ao validar token de recuperação no Redis: {e}")
            return None

    def invalidar_token(self, token: str) -> None:
        """Invalida o token (ex: após o uso) para garantir que seja de uso único."""
        chave_token = f"{self.prefix_token_to_email}{token}"
        try:
            email = self.redis_client.get(chave_token)

            if email:
                if isinstance(email, bytes):
                    email = email.decode("utf-8")

                chave_email = f"{self.prefix_email_to_token}{email}"
                self.redis_client.delete(chave_token)
                self.redis_client.delete(chave_email)
        except redis.RedisError as e:
            logger.error(f"Erro ao invalidar token de recuperação no Redis: {e}")
