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

FILES_CHANGED=$(wc -l < "$GEMINI_DIR/changed-files.txt")
echo "📊 Volume de arquivos: $FILES_CHANGED"

if [ "$FILES_CHANGED" -gt 10 ]; then
  echo "⚠️  Alto volume detectado. Gerando diff limpo (ignoring whitespace)..."
  # Tenta identificar a base branch para o diff local
  BASE_BRANCH=$(gh pr view "$PR_NUMBER" --json baseRefName --template '{{.baseRefName}}')
  git diff -w "$BASE_BRANCH...HEAD" > "$GEMINI_DIR/pr-clean-diff.txt" || echo "Não foi possível gerar diff local" > "$GEMINI_DIR/pr-clean-diff.txt"
fi

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
  echo "🧪 Executando validações de BACKEND via scripts/ci/backend.sh..."
  BACKEND_RUN="true"
  
  # Executa o script oficial de CI do backend
  # Redirecionamos a saída para o log, mas capturamos o exit code
  if "$REPO_ROOT/scripts/ci/backend.sh" >> "$LOG_FILE" 2>&1; then
    BACKEND_LINT="PASS"
    BACKEND_FORMAT="PASS"
    BACKEND_PYTEST="PASS"
  else
    # Se falhou, tentamos identificar onde para o JSON (opcionalmente)
    # Por simplicidade, marcamos como FAIL se o script unificado falhar
    BACKEND_LINT="FAIL"
    BACKEND_FORMAT="FAIL"
    BACKEND_PYTEST="FAIL"
    echo "❌ Falha na validação do Backend. Veja .gemini/pr-validation.log"
  fi
fi

if [ "$RUN_FRONTEND" = true ]; then
  echo "🧪 Executando validações de FRONTEND via scripts/ci/frontend.sh..."
  FRONTEND_RUN="true"
  
  if "$REPO_ROOT/scripts/ci/frontend.sh" >> "$LOG_FILE" 2>&1; then
    FRONTEND_TSC="PASS"
    FRONTEND_LINT="PASS"
    FRONTEND_VITEST="PASS"
    FRONTEND_BUILD="PASS"
  else
    FRONTEND_TSC="FAIL"
    FRONTEND_LINT="FAIL"
    FRONTEND_VITEST="FAIL"
    FRONTEND_BUILD="FAIL"
    echo "❌ Falha na validação do Frontend. Veja .gemini/pr-validation.log"
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
