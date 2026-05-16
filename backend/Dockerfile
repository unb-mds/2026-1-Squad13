FROM python:3.12-slim

# Instala dependências do sistema necessárias para compilar pacotes (se necessário)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala o uv para gerenciar dependências
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de configuração de dependências
COPY pyproject.toml uv.lock ./

# Instala as dependências
RUN uv sync --frozen --no-install-project

# Copia o código fonte
COPY src ./src

# Expõe a porta do FastAPI
EXPOSE 8000

# Define o PYTHONPATH para incluir a pasta src
ENV PYTHONPATH=/app/src

# Comando para rodar a aplicação
# Usamos 'fastapi dev' para ambiente de desenvolvimento com reload automático
CMD ["uv", "run", "fastapi", "dev", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
