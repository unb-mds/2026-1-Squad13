#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"
cd "${PROJECT_ROOT}/frontend"

log_info "[FRONTEND] Instalando dependências (se necessário)..."
# Ideal rodar npm ci se houver package-lock.json
if [ -f "package-lock.json" ]; then
    npm ci >/dev/null 2>&1
else
    npm install >/dev/null 2>&1
fi

log_info "[FRONTEND] Checando Tipos (TSC)..."
npx tsc --noEmit

log_info "[FRONTEND] Rodando Linter..."
npm run lint

log_info "[FRONTEND] Rodando Testes..."
npm run test -- --run

log_info "[FRONTEND] Checando Build..."
npm run build

log_success "[FRONTEND] Passou em todos os checks!"
