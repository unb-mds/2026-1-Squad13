#!/usr/bin/env bash
# Gera um resumo estatístico da auditoria.

NUM_FILES=$(find frontend/src -name "*.tsx" | wc -l)
NUM_DOCS=$(find docs/frontend -name "*.md" | wc -l)
HARDCODED_COLORS=$(grep -r "bg-\[#" frontend/src | wc -l)

echo "📊 Resumo Estatístico da Auditoria:"
echo "- Arquivos React: $NUM_FILES"
echo "- Documentos: $NUM_DOCS"
echo "- Potenciais cores hardcoded detectadas: $HARDCODED_COLORS"
