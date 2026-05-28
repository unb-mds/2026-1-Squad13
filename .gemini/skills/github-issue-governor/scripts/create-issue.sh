#!/usr/bin/env bash
set -euo pipefail

# Script aprimorado para criação de issues com templates e busca de duplicados.
# Uso: ./create-issue.sh "Título da Issue" "<template_name ou body_file>" "labels"

TITLE="${1:-}"
TEMPLATE_OR_BODY="${2:-}"
LABELS="${3:-}"

if [ -z "$TITLE" ] || [ -z "$TEMPLATE_OR_BODY" ] || [ -z "$LABELS" ]; then
  echo "Erro: Parâmetros insuficientes."
  echo "Uso: $0 \"<Título>\" \"<template_name ou body_file>\" \"<labels>\""
  echo "Templates disponíveis: bug, feature, refactor, technical-debt, ou qualquer arquivo .md em templates/"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/../templates"

# 1. Resolução do Body/Template
RESOLVED_BODY=""
if [ -f "$TEMPLATE_OR_BODY" ]; then
  RESOLVED_BODY="$TEMPLATE_OR_BODY"
elif [ -f "$TEMPLATES_DIR/$TEMPLATE_OR_BODY" ]; then
  RESOLVED_BODY="$TEMPLATES_DIR/$TEMPLATE_OR_BODY"
elif [ -f "$TEMPLATES_DIR/$TEMPLATE_OR_BODY.md" ]; then
  RESOLVED_BODY="$TEMPLATES_DIR/$TEMPLATE_OR_BODY.md"
else
  echo "Erro: Template ou arquivo de corpo '$TEMPLATE_OR_BODY' não encontrado."
  echo "Buscado em: $TEMPLATE_OR_BODY ou $TEMPLATES_DIR/$TEMPLATE_OR_BODY[.md]"
  exit 1
fi

# 2. Validação das Labels Obrigatórias
echo "🔍 Validando labels..."
if ! "$SCRIPT_DIR/validate-labels.sh" "$LABELS"; then
  echo "❌ Validação de labels falhou. Por favor, corrija as labels conforme a governança."
  exit 1
fi

# 3. Verificação de Issues Duplicadas
echo "🔍 Verificando issues abertas para evitar duplicidades..."
if command -v gh &> /dev/null; then
  # Tenta listar issues abertas, trata falhas de autenticação com resiliência
  if OPEN_ISSUES_JSON=$(gh issue list --state open --limit 200 --json number,title,labels,url 2>/dev/null); then
    # Executa o script Python passando a lista JSON via stdin
    set +e
    python3 "$SCRIPT_DIR/check-duplicate-issues.py" "$TITLE" <<< "$OPEN_ISSUES_JSON"
    DUP_EXIT_CODE=$?
    set -e
    
    if [ $DUP_EXIT_CODE -eq 2 ]; then
      # Encontrou possíveis duplicados
      if [ -t 0 ]; then
        # Se for um terminal interativo (TTY), pergunta ao usuário
        read -p "⚠️ Deseja prosseguir com a criação da issue mesmo assim? (s/N): " -r RESPONSE
        if [[ ! "$RESPONSE" =~ ^[sS]$ ]]; then
          echo "Abortado pelo usuário."
          exit 0
        fi
      else
        echo "⚠️ Atenção: Rodando em modo não-interativo. A issue será criada apesar dos possíveis duplicados acima."
      fi
    elif [ $DUP_EXIT_CODE -ne 0 ]; then
      echo "⚠️ Aviso: Ocorreu um erro ao executar o validador de duplicados (exit code $DUP_EXIT_CODE). Prosseguindo..."
    fi
  else
    echo "⚠️ Aviso: Não foi possível obter as issues do GitHub (gh CLI não autenticada?). Pulando verificação de duplicados..."
  fi
else
  echo "⚠️ Aviso: gh CLI não encontrada no PATH. Pulando verificação de duplicados..."
fi

# 4. Criação da Issue
echo "🚀 Criando issue no GitHub..."
CREATED_URL=$(gh issue create \
  --title "$TITLE" \
  --body-file "$RESOLVED_BODY" \
  --label "$LABELS")

echo "✅ Issue criada com sucesso!"
echo "🔗 URL: $CREATED_URL"
