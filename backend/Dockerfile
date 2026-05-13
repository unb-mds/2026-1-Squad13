FROM python:3.12-slim

# Instala o uv para gerenciar dependências
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de configuração de dependências
COPY pyproject.toml uv.lock ./

# Instala as dependências (sem instalar o projeto em si primeiro para aproveitar o cache do Docker)
RUN uv sync --frozen --no-install-project

# Copia o código fonte
COPY src ./src

# Expõe a porta do FastAPI
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uv", "run", "fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
