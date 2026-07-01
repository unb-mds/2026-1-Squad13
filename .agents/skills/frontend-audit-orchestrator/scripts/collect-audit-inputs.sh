#!/usr/bin/env bash
# Coleta os principais artefatos do frontend para análise.

echo "📦 Coletando insumos para auditoria..."
echo "---"
echo "Configuração Tailwind:"
cat frontend/tailwind.config.js | grep -A 20 "colors:"
echo "---"
echo "Estrutura de Features:"
ls -R frontend/src/features | grep ":"
echo "---"
echo "Componentes Compartilhados (Shared):"
ls -R frontend/src/shared | grep ":"
echo "---"
echo "Documentação Recente:"
ls -t docs/frontend | head -n 10
