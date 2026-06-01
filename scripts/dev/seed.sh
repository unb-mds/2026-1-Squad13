#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

SEED_TYPE="bootstrap"
LIMIT="10"

show_help() {
    echo "Uso: $0 [OPÇÕES]"
    echo "Popula o banco de dados."
    echo ""
    echo "Opções:"
    echo "  --type <tipo>   bootstrap, sample, ou sync (padrão: bootstrap)"
    echo "  --limit <n>     Quantidade de registros (padrão: 10)"
    echo "  --help          Mostra esta mensagem"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --help) show_help; exit 0 ;;
        --type) SEED_TYPE="$2"; shift 2 ;;
        --limit) LIMIT="$2"; shift 2 ;;
        *) log_error "Argumento inválido: $1"; show_help; exit 1 ;;
    esac
done

cd "$PROJECT_ROOT"
log_info "Executando seed ($SEED_TYPE, limit: $LIMIT)..."
docker compose exec -T backend uv run python src/seed.py --type "$SEED_TYPE" --limit "$LIMIT"
log_success "Seed finalizado."
