#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

cd "$PROJECT_ROOT"
log_info "Aplicando migrations (Alembic)..."
docker compose run --rm -T backend uv run alembic upgrade head
log_success "Migrations aplicadas com sucesso."

log_info "Rodando backfill de emendas (Issue 253)..."
docker compose run --rm -T backend uv run python src/backfill_issue_253.py
log_success "Backfill concluído."
