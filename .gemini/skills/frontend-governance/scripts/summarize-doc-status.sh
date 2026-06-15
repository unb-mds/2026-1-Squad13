#!/usr/bin/env bash
# Script para resumir o estado dos documentos de frontend.

echo "📊 Status da Documentação Frontend:"
echo "-----------------------------------"
find docs/frontend -name "*.md" | while read -r file; do
    LAST_MOD=$(git log -1 --format="%cd" --date=short "$file" 2>/dev/null || echo "Não versionado")
    echo "- $(basename "$file"): Atualizado em $LAST_MOD"
done
