#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

cd "$PROJECT_ROOT"
log_info "Iniciando Validação Full-Stack..."

"$PROJECT_ROOT/scripts/ci/backend.sh"
"$PROJECT_ROOT/scripts/ci/frontend.sh"

log_success "PROJETO 100% VALIDADO!"
