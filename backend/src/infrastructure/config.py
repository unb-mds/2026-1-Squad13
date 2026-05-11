from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Gerencia as configurações da aplicação.
    As variáveis são lidas do ambiente ou de um arquivo .env.
    """
    model_config = SettingsConfigDict(
        env_file=".env", # Procura na pasta atual
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Variáveis com valores padrão para facilitar o dev local
    POSTGRES_DB: str = "monitor_db"
    POSTGRES_USER: str = "app_user"
    POSTGRES_PASSWORD: str = "senha123"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    @property
    def database_url(self) -> str:
        """Gera a URL de conexão para o SQLAlchemy/SQLModel"""
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

# Instância global para ser usada no projeto
settings = Settings()
