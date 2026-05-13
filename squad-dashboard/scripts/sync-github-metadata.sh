#!/bin/bash

# Script de Sincronização de Metadados (Labels e Assignees)
# Uso: GITHUB_TOKEN=seu_novo_token ./sync-github-metadata.sh

REPO="unb-mds/2026-1-Squad13"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Erro: A variável GITHUB_TOKEN não está definida."
    exit 1
fi

update_issue() {
    local issue_number=$1
    local assignee=$2
    local label=$3

    echo "Atualizando Issue #$issue_number (Assignee: $assignee, Label: $label)..."
    
    curl -s -X PATCH -H "Authorization: token $GITHUB_TOKEN" \
         -H "Accept: application/vnd.github+json" \
         https://api.github.com/repos/$REPO/issues/$issue_number \
         -d "{\"assignees\":[\"$assignee\"], \"labels\":[\"$label\", \"chore\"]}" > /dev/null
}

# --- MAPEAMENTO DO PLANO DE AÇÃO ---

# F3: Dashboard Analítico (caioflmjr)
for i in 58 57 56 55 54 53 52 50 49 48 47; do update_issue $i "caioflmjr" "feat:f3"; done

# F6: Infraestrutura & Arquitetura (kaiky-yun)
for i in 45 42 41 38 35 30 29 28; do update_issue $i "kaiky-yun" "feat:f6"; done

# F7: Qualidade & CI/CD (kaiky-yun)
for i in 33 32 31; do update_issue $i "kaiky-yun" "feat:f7"; done

# F1: Consulta de Proposições (Atribuição mista/kaiky-yun por volume de commits)
for i in 46 40 39 36 34; do update_issue $i "kaiky-yun" "feat:f1"; done

# F2: Detalhamento (kaiky-yun)
update_issue 43 "kaiky-yun" "feat:f2"

# F5: Autenticação (kaiky-yun)
update_issue 44 "kaiky-yun" "feat:f5"

echo "Concluído! Todas as issues foram sincronizadas conforme o plano de ação."
