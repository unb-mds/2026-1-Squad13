#!/usr/bin/env bash
set -euo pipefail

# Script para executar e validar a semente de banco de dados (seed.py)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../" && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"

echo "🌱 Validando e executando semente (seed) de dados..."

if [ ! -d "$BACKEND_DIR" ]; then
  echo "Erro: Diretório backend não encontrado em $BACKEND_DIR" >&2
  exit 1
fi

set +e
(cd "$BACKEND_DIR" && export PYTHONPATH=src && uv run python src/seed.py)
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Semente aplicada/verificada com sucesso!"
else
  echo "❌ Falha ao aplicar a semente de dados."
  echo "Dica: Verifique a conexão com o banco ou com os adaptadores de APIs."
  exit $EXIT_CODE
fi
