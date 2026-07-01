#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"
ensure_env_file

cd "$PROJECT_ROOT"
log_info "Aplicando migrations (Alembic)..."
docker compose run --rm -T backend uv run alembic upgrade head
log_success "Migrations aplicadas com sucesso."

log_info "Disparando backfill de emendas em background (Issue 253)..."
docker compose run --rm -T backend uv run python src/trigger_backfill.py
log_success "Backfill enfileirado com sucesso."
