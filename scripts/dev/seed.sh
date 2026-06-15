#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"
ensure_env_file

cd "$PROJECT_ROOT"
log_info "Acionando o preenchimento de lacunas no Celery..."
docker compose exec -T backend uv run python src/trigger_seed.py
