#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

show_help() {
    echo "Uso: $0 [OPÇÕES]"
    echo "Inicia o ambiente na GCP."
    echo ""
    echo "Opções:"
    echo "  --ip <IP>       Fornece o IP externo da VM GCP"
    echo "  --help          Mostra esta mensagem"
}

GCP_IP="${GCP_IP:-}"

while [[ $# -gt 0 ]]; do
    case $1 in
        --help) show_help; exit 0 ;;
        --ip) GCP_IP="$2"; shift 2 ;;
        *) log_error "Argumento inválido: $1"; show_help; exit 1 ;;
    esac
done

cd "$PROJECT_ROOT"
require_cmd docker

if [ -z "$GCP_IP" ]; then
    read -p "Qual é o IP externo da VM GCP? (ex: 34.x.x.x): " GCP_IP
fi

if [ -z "$GCP_IP" ]; then
    log_error "IP externo não informado."
    exit 1
fi

ensure_env_file

ENV_GCP="${PROJECT_ROOT}/.env.gcp"
log_info "Criando arquivo ${ENV_GCP} temporário..."
cp "${PROJECT_ROOT}/.env" "$ENV_GCP"
echo -e "\n# Variaveis GCP Override" >> "$ENV_GCP"
echo "VITE_API_URL=http://${GCP_IP}:8000" >> "$ENV_GCP"
echo "ALLOWED_ORIGINS=http://${GCP_IP}:5173" >> "$ENV_GCP"

COMPOSE_FILES="-f docker-compose.yml -f docker-compose.gcp.yml"

log_info "Subindo ambiente GCP (IP: ${GCP_IP})..."
# Utiliza --wait para aguardar healthchecks e evitar polling manual no bash
docker compose $COMPOSE_FILES --env-file "$ENV_GCP" --profile worker up -d --build --wait

log_info "Rodando migrations..."
"$PROJECT_ROOT/scripts/db/migrate.sh"

log_success "Ambiente GCP Online!"
log_info "Frontend: http://${GCP_IP}:5173"
log_info "Backend:  http://${GCP_IP}:8000"
log_warn "Nota: O arquivo .env.gcp foi gerado para debug. Você pode removê-lo se desejar."
