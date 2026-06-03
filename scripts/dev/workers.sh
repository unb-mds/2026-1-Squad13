#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

cd "$PROJECT_ROOT"
log_info "Iniciando workers Celery em background..."
docker compose up -d --profile worker celery_worker celery_beat
log_success "Workers online."
