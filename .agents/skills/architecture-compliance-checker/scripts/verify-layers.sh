#!/usr/bin/env bash
set -euo pipefail

# Script wrapper para verificar limites das camadas arquiteturais

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../" && pwd)"
AGENT_SCRATCH_DIR="$REPO_ROOT/.agents/scratch"

FILES_TO_CHECK=()

if [ $# -gt 0 ]; then
  # Se argumentos forem fornecidos, use-os
  for arg in "$@"; do
    FILES_TO_CHECK+=("$arg")
  done
elif [ -f "$AGENT_SCRATCH_DIR/changed-files.txt" ]; then
  # Senão, use os arquivos alterados da PR registrados
  while IFS= read -r file; do
    if [ -f "$REPO_ROOT/$file" ]; then
      FILES_TO_CHECK+=("$REPO_ROOT/$file")
    fi
  done < "$AGENT_SCRATCH_DIR/changed-files.txt"
else
  # Se não houver arquivo, verifica recursivamente a pasta backend/src
  echo "Aviso: Sem argumentos e sem changed-files.txt. Verificando toda a pasta backend/src/..."
  while IFS= read -r -d '' file; do
    FILES_TO_CHECK+=("$file")
  done < <(find "$REPO_ROOT/backend/src" -name "*.py" -print0)
fi

if [ ${#FILES_TO_CHECK[@]} -eq 0 ]; then
  echo "Nenhum arquivo Python elegível para checagem de imports."
  exit 0
fi

echo "🔍 Verificando acoplamento de camadas em ${#FILES_TO_CHECK[@]} arquivo(s)..."
set +e
python3 "$SCRIPT_DIR/check-imports.py" "${FILES_TO_CHECK[@]}"
EXIT_CODE=$?
set -e

exit $EXIT_CODE
