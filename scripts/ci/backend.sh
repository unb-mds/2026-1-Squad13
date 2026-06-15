#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"
cd "${PROJECT_ROOT}/backend"

export PYTHONPATH=src

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
