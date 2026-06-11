#!/usr/bin/env bash
set -euo pipefail

# Script de apoio para revisão de PR via gh CLI
# Uso típico: review‑pr.sh 121

PR_NUMBER="${1:-}"

if [ -z "$PR_NUMBER" ]; then
  echo "Erro: Número da PR não fornecido."
  echo "Uso: $0 <numero_da_pr>"
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"

# Garante que o diretório .gemini existe para arquivos temporários
mkdir -p "$REPO_ROOT/.gemini"

echo "📦 Coletando contexto da PR #$PR_NUMBER..."
gh pr view "$PR_NUMBER" \
  --json number,title,body,files,comments,reviews,reviewDecision,changedFiles,url,baseRefName,headRefName \
  > "$REPO_ROOT/.gemini/pr-context.json"

echo "📄 Listando arquivos alterados..."
gh pr diff "$PR_NUMBER" --name-only > "$REPO_ROOT/.gemini/changed-files.txt"

echo "✅ Arquivos de contexto gerados em .gemini/."

echo "Hint: no Gemini CLI, ative a skill pr-reviewer e peça:"
echo "      'Analise a PR #$PR_NUMBER deste repositório'"
