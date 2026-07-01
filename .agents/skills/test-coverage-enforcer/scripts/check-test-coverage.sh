#!/usr/bin/env bash
set -euo pipefail

# Script para garantir presença de arquivos de teste correspondentes e rodar cobertura

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../" && pwd)"
AGENT_SCRATCH_DIR="$REPO_ROOT/.agents/scratch"
BACKEND_DIR="$REPO_ROOT/backend"

MISSING_TESTS=()
CHECKED_COUNT=0

echo "🔍 Verificando presença de arquivos de teste para os arquivos alterados..."

if [ -f "$AGENT_SCRATCH_DIR/changed-files.txt" ]; then
  while IFS= read -r file; do
    # Apenas arquivos Python dentro de backend/src/ (exceto __init__.py e arquivos de configuração)
    if [[ "$file" == backend/src/domain/* || "$file" == backend/src/application/* ]] && [[ "$file" == *.py ]] && [[ "$file" != *__init__.py ]]; then
      CHECKED_COUNT=$((CHECKED_COUNT + 1))
      BASENAME=$(basename "$file" .py)
      
      # Procura por um arquivo de teste contendo o nome base do arquivo na pasta tests/
      TEST_FOUND=false
      if find "$BACKEND_DIR/tests" -name "*test_$BASENAME.py" -print -quit | grep -q .; then
        TEST_FOUND=true
      fi
      
      if [ "$TEST_FOUND" = false ]; then
        MISSING_TESTS+=("$file")
      fi
    fi
  done < "$AGENT_SCRATCH_DIR/changed-files.txt"
fi

if [ ${#MISSING_TESTS[@]} -gt 0 ]; then
  echo "⚠️ AVISO: Foram encontrados novos módulos sem arquivo de teste correspondente:"
  echo "----------------------------------------------------------------------"
  for m in "${MISSING_TESTS[@]}"; do
    echo "- Módulo: $m"
    echo "  (Esperado correspondente em: backend/tests/unit/test_$(basename "$m") ou similar)"
  done
  echo "----------------------------------------------------------------------"
else
  if [ $CHECKED_COUNT -gt 0 ]; then
    echo "✅ Todos os $CHECKED_COUNT módulo(s) alterado(s) possuem arquivos de teste correspondentes!"
  else
    echo "Nenhum arquivo Python em domain/ ou application/ alterado para verificar."
  fi
fi

# Executa relatório de cobertura de testes do backend
echo "🧪 Executando testes e computando cobertura do Backend..."
if [ -d "$BACKEND_DIR" ]; then
  set +e
  # Executa pytest com cobertura
  (cd "$BACKEND_DIR" && export PYTHONPATH=src && uv run pytest --cov=src --cov-report=term-missing)
  EXIT_CODE=$?
  set -e
  
  if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Cobertura computada com sucesso e testes passando!"
  else
    echo "❌ Falha na execução dos testes do backend."
    exit $EXIT_CODE
  fi
else
  echo "Erro: pasta backend/ não encontrada para rodar pytest."
  exit 1
fi
