#!/usr/bin/env bash
set -euo pipefail

# Script para reinicializar o banco de dados e aplicar o DDL das tabelas

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../" && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"

echo "🔄 Reinicializando tabelas do banco de dados local..."

if [ ! -d "$BACKEND_DIR" ]; then
  echo "Erro: Diretório backend não encontrado em $BACKEND_DIR" >&2
  exit 1
fi

set +e
(cd "$BACKEND_DIR" && export PYTHONPATH=src && uv run python src/init_db.py)
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Banco de dados inicializado com sucesso!"
else
  echo "❌ Falha ao inicializar o banco de dados."
  echo "Dica: Verifique se os containers do Docker estão rodando ('docker compose up -d') e se as credenciais do .env estão corretas."
  exit $EXIT_CODE
fi
