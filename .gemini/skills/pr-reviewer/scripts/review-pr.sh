#!/usr/bin/env bash
set -euo pipefail

# Script de apoio para revisão de PR via gh CLI com validação local
# Uso: ./review-pr.sh <numero_da_pr>

PR_NUMBER="${1:-}"

if [ -z "$PR_NUMBER" ]; then
  echo "Erro: Número da PR não fornecido."
  echo "Uso: $0 <numero_da_pr>"
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
GEMINI_DIR="$REPO_ROOT/.gemini"

# Garante que o diretório .gemini existe
mkdir -p "$GEMINI_DIR"

echo "📦 Coletando contexto da PR #$PR_NUMBER..."
gh pr view "$PR_NUMBER" \
  --json number,title,body,files,comments,reviews,reviewDecision,changedFiles,url,baseRefName,headRefName \
  > "$GEMINI_DIR/pr-context.json"

echo "📄 Listando arquivos alterados..."
gh pr diff "$PR_NUMBER" --name-only > "$GEMINI_DIR/changed-files.txt"

echo "✅ Arquivos de contexto gerados."

# Determina o escopo das alterações
RUN_BACKEND=false
RUN_FRONTEND=false

while IFS= read -r file; do
  if [[ "$file" == backend/* ]]; then
    RUN_BACKEND=true
  elif [[ "$file" == frontend/* ]]; then
    RUN_FRONTEND=true
  fi
done < "$GEMINI_DIR/changed-files.txt"

# Limpa logs anteriores
LOG_FILE="$GEMINI_DIR/pr-validation.log"
JSON_FILE="$GEMINI_DIR/pr-validation.json"
echo "=== PR #$PR_NUMBER VALIDATION LOG ===" > "$LOG_FILE"
date >> "$LOG_FILE"

# Inicializa variáveis de status
BACKEND_RUN="false"
BACKEND_LINT="SKIPPED"
BACKEND_FORMAT="SKIPPED"
BACKEND_PYTEST="SKIPPED"

FRONTEND_RUN="false"
FRONTEND_TSC="SKIPPED"
FRONTEND_LINT="SKIPPED"
FRONTEND_VITEST="SKIPPED"
FRONTEND_BUILD="SKIPPED"

if [ "$RUN_BACKEND" = true ]; then
  echo "🧪 Executando validações de BACKEND..."
  BACKEND_RUN="true"
  
  # 1. Linter
  echo "--- BACKEND RUFF CHECK ---" >> "$LOG_FILE"
  if (cd "$REPO_ROOT/backend" && export PYTHONPATH=src && uv run ruff check .) >> "$LOG_FILE" 2>&1; then
    BACKEND_LINT="PASS"
  else
    BACKEND_LINT="FAIL"
  fi
  
  # 2. Formatação
  echo "--- BACKEND RUFF FORMAT ---" >> "$LOG_FILE"
  if (cd "$REPO_ROOT/backend" && export PYTHONPATH=src && uv run ruff format --check .) >> "$LOG_FILE" 2>&1; then
    BACKEND_FORMAT="PASS"
  else
    BACKEND_FORMAT="FAIL"
  fi
  
  # 3. Testes
  echo "--- BACKEND PYTEST ---" >> "$LOG_FILE"
  if (cd "$REPO_ROOT/backend" && export PYTHONPATH=src && uv run pytest) >> "$LOG_FILE" 2>&1; then
    BACKEND_PYTEST="PASS"
  else
    BACKEND_PYTEST="FAIL"
  fi
fi

if [ "$RUN_FRONTEND" = true ]; then
  echo "🧪 Executando validações de FRONTEND..."
  FRONTEND_RUN="true"
  
  # 1. TSC (Tipagem)
  echo "--- FRONTEND TSC CHECK ---" >> "$LOG_FILE"
  if (cd "$REPO_ROOT/frontend" && npx tsc --noEmit) >> "$LOG_FILE" 2>&1; then
    FRONTEND_TSC="PASS"
  else
    FRONTEND_TSC="FAIL"
  fi
  
  # 2. ESLint
  echo "--- FRONTEND ESLINT ---" >> "$LOG_FILE"
  if (cd "$REPO_ROOT/frontend" && npm run lint) >> "$LOG_FILE" 2>&1; then
    FRONTEND_LINT="PASS"
  else
    FRONTEND_LINT="FAIL"
  fi
  
  # 3. Vitest
  echo "--- FRONTEND VITEST ---" >> "$LOG_FILE"
  if (cd "$REPO_ROOT/frontend" && npm run test -- --run) >> "$LOG_FILE" 2>&1; then
    FRONTEND_VITEST="PASS"
  else
    FRONTEND_VITEST="FAIL"
  fi
  
  # 4. Build check
  echo "--- FRONTEND BUILD CHECK ---" >> "$LOG_FILE"
  if (cd "$REPO_ROOT/frontend" && npm run build) >> "$LOG_FILE" 2>&1; then
    FRONTEND_BUILD="PASS"
  else
    FRONTEND_BUILD="FAIL"
  fi
fi

# Cria o arquivo de status JSON
cat <<EOF > "$JSON_FILE"
{
  "pr": $PR_NUMBER,
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "backend": {
    "run": $BACKEND_RUN,
    "lint": "$BACKEND_LINT",
    "format": "$BACKEND_FORMAT",
    "pytest": "$BACKEND_PYTEST"
  },
  "frontend": {
    "run": $FRONTEND_RUN,
    "tsc": "$FRONTEND_TSC",
    "lint": "$FRONTEND_LINT",
    "vitest": "$FRONTEND_VITEST",
    "build": "$FRONTEND_BUILD"
  }
}
EOF

echo "✅ Validações locais concluídas."
echo "📝 Resultados gravados em:"
echo "   - Log detalhado: .gemini/pr-validation.log"
echo "   - Status estruturado: .gemini/pr-validation.json"
echo ""
echo "Hint: no Gemini CLI, peça:"
echo "      'Analise a PR #$PR_NUMBER deste repositório'"
