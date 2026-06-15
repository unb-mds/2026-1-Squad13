#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

cd "$PROJECT_ROOT"
log_info "Inicializando tabela e infraestruturas do Banco de Dados..."
docker compose exec -T backend uv run python src/init_db.py
log_success "Banco inicializado."
