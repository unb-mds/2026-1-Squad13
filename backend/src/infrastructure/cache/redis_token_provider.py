import redis
import uuid
from typing import Optional
from application.ports.password_reset_token_provider import PasswordResetTokenProvider


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

        # Invalida token anterior se existir
        token_antigo_bytes = self.redis_client.get(chave_email)
        if token_antigo_bytes:
            token_antigo = token_antigo_bytes.decode("utf-8")
            chave_token_antigo = f"{self.prefix_token_to_email}{token_antigo}"
            self.redis_client.delete(chave_token_antigo)

        # Salva o novo token
        chave_novo_token = f"{self.prefix_token_to_email}{novo_token}"
        self.redis_client.setex(chave_novo_token, self.ttl_seconds, email)

        # Atualiza o mapeamento de email para o token atual
        self.redis_client.setex(chave_email, self.ttl_seconds, novo_token)

        return novo_token

    def validar_token(self, token: str) -> Optional[str]:
        """Valida o token e retorna o e-mail associado, ou None se inválido/expirado."""
        chave_token = f"{self.prefix_token_to_email}{token}"
        email_bytes = self.redis_client.get(chave_token)
        if email_bytes:
            return email_bytes.decode("utf-8")
        return None

    def invalidar_token(self, token: str) -> None:
        """Invalida o token (ex: após o uso) para garantir que seja de uso único."""
        chave_token = f"{self.prefix_token_to_email}{token}"
        email_bytes = self.redis_client.get(chave_token)

        if email_bytes:
            email = email_bytes.decode("utf-8")
            chave_email = f"{self.prefix_email_to_token}{email}"
            self.redis_client.delete(chave_token)
            self.redis_client.delete(chave_email)
