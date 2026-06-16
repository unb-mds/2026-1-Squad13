from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Gerencia as configurações da aplicação.
    As variáveis são lidas do ambiente ou de um arquivo .env.
    """

    # Limite para relevância estatística na estimativa (MVP = 50)
    THRESHOLD_MINIMO_AMOSTRA_ESTIMATIVA: int = 50

    model_config = SettingsConfigDict(
        # Procura primeiro no local, depois sobe para a raiz do projeto
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Variáveis com valores padrão para facilitar o dev local
    POSTGRES_DB: str = "monitor_db"
    POSTGRES_USER: str = "app_user"
    POSTGRES_PASSWORD: str = "senha123"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Segurança e JWT
    SECRET_KEY: str = "sua-chave-secreta-de-desenvolvimento-muito-segura"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

    # Redis e Bloqueio de Conta
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    TENTATIVAS_MAXIMAS: int = 5
    BLOQUEIO_MINUTOS: int = 15

    # Token secreto para endpoints internos (GitHub Actions cron)
    INTERNAL_API_SECRET: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> list[str]:
        """Processa a string separada por vírgula em uma lista limpa."""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def database_url(self) -> str:
        """Gera a URL de conexão para o SQLAlchemy/SQLModel"""
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        """Gera a URL de conexão para o Redis"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# Instância global para ser usada no projeto
settings = Settings()
