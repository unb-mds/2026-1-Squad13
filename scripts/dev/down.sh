#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"
ensure_env_file

cd "$PROJECT_ROOT"
log_info "Derrubando ambiente local..."
# Garante a limpeza de recursos de workers (evitando "Network is in use")
docker compose --profile worker down --remove-orphans
log_success "Ambiente desligado e limpo."
