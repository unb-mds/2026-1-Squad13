#!/usr/bin/env bash
# Script para localizar documentos de frontend relevantes para uma tarefa.

SEARCH_TERM=$1
DOCS_DIR="docs/frontend"

if [ -z "$SEARCH_TERM" ]; then
  echo "Uso: $0 <termo_de_busca>"
  exit 1
fi

echo "🔍 Buscando contexto para: '$SEARCH_TERM'..."
grep -rli "$SEARCH_TERM" "$DOCS_DIR"
