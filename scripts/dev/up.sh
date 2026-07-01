#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

show_help() {
    echo "Uso: $0 [OPÇÕES]"
    echo "Inicia o ambiente de desenvolvimento local."
    echo ""
    echo "Opções:"
    echo "  --no-workers    Inicia sem os workers do Celery"
    echo "  --help          Mostra esta mensagem"
}

WORKER_PROFILE="--profile worker"

for arg in "$@"; do
    case $arg in
        --help) show_help; exit 0 ;;
        --no-workers) WORKER_PROFILE=""; shift ;;
        *) log_error "Argumento inválido: $arg"; show_help; exit 1 ;;
    esac
done

cd "$PROJECT_ROOT"
require_cmd docker

if ! docker ps > /dev/null 2>&1; then
    log_error "Sem permissão no Docker. Use sudo ou configure seu usuário."
    exit 1
fi

ensure_env_file

log_info "Subindo infraestrutura local..."
# O --wait faz o docker compose aguardar os healthchecks
docker compose $WORKER_PROFILE up -d --build --wait

log_success "Ambiente de Desenvolvimento pronto!"
log_info "Frontend: http://localhost:5173"
log_info "Backend:  http://localhost:8000"
