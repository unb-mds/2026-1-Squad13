#!/usr/bin/env bash
set -euo pipefail

# Cores para o output
export GREEN='\033[0;32m'
export RED='\033[0;31m'
export BLUE='\033[0;34m'
export YELLOW='\033[1;33m'
export NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO] $1${NC}"; }
log_success() { echo -e "${GREEN}[SUCCESS] $1${NC}"; }
log_warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
log_error() { echo -e "${RED}[ERROR] $1${NC}" >&2; }

# Obtém a raiz do projeto de forma robusta
get_project_root() {
    local dir
    dir="$(dirname "${BASH_SOURCE[0]}")"
    cd "$dir/.." >/dev/null 2>&1 && pwd
}

export PROJECT_ROOT=$(get_project_root)

# Trap de erros para facilitar debug
trap_error() {
    local line=$1
    local cmd=$2
    log_error "Falha na linha $line: $cmd"
}
trap 'trap_error ${LINENO} "$BASH_COMMAND"' ERR

require_cmd() {
    local cmd=$1
    if ! command -v "$cmd" >/dev/null 2>&1; then
        log_error "Comando obrigatório não encontrado: $cmd"
        exit 1
    fi
}

ensure_env_file() {
    local env_file="${PROJECT_ROOT}/.env"
    local example_file="${PROJECT_ROOT}/.env.example"

    if [ ! -f "$env_file" ]; then
        log_warn "Arquivo .env não encontrado. Criando a partir de .env.example..."
        if [ -f "$example_file" ]; then
            cp "$example_file" "$env_file"
            log_success ".env criado com sucesso."
        else
            log_error ".env.example não encontrado."
            exit 1
        fi
    fi
}
