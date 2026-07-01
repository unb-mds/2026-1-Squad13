#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"
cd "${PROJECT_ROOT}/backend"

export PYTHONPATH=src

# Fallback dinâmico: se 'uv' não estiver disponível localmente no host, roda via Docker exec
if ! command -v uv &> /dev/null; then
    log_info "Gerenciador 'uv' não encontrado localmente no PATH. Tentando rodar validações via Docker..."
    if [ "$(docker ps -q -f name=monitor_backend)" ]; then
        log_info "[DOCKER-BACKEND] Rodando Linter (Ruff)..."
        docker exec -t monitor_backend uv run ruff check .

        log_info "[DOCKER-BACKEND] Verificando Formatação..."
        if ! docker exec -t monitor_backend uv run ruff format --check . >/dev/null 2>&1; then
            log_warn "O código possui problemas de formatação. Execute 'docker exec -it monitor_backend uv run ruff format .'."
        fi

        log_info "[DOCKER-BACKEND] Checando Syntax Compilation..."
        docker exec -t monitor_backend uv run python -m py_compile src/main.py

        log_info "[DOCKER-BACKEND] Rodando Pytest (exceto integração externa)..."
        docker exec -t -e PYTHONPATH=src monitor_backend uv run pytest -m "not integration"

        log_success "[BACKEND] Passou em todos os checks via Docker!"
        exit 0
    else
        log_error "Erro: 'uv' não está instalado no host e o container 'monitor_backend' não está em execução."
        exit 1
    fi
fi

log_info "[BACKEND] Rodando Linter (Ruff)..."
uv run ruff check .

log_info "[BACKEND] Verificando Formatação..."
if ! uv run ruff format --check . >/dev/null 2>&1; then
    log_warn "O código possui problemas de formatação. Execute 'uv run ruff format .'."
fi

log_info "[BACKEND] Checando Syntax Compilation..."
uv run python -m py_compile src/main.py

log_info "[BACKEND] Rodando Pytest (exceto integração externa)..."
uv run pytest -m "not integration"

log_success "[BACKEND] Passou em todos os checks!"
