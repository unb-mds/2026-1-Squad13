#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"
ensure_env_file

SOURCE=""
LIMIT=""
FORCE=""
YEARS=""
TYPES=""

show_help() {
    echo "Uso: $0 [OPÇÕES]"
    echo "Popula o banco de dados com dados reais das APIs legislativas."
    echo ""
    echo "Opções (se nenhuma for passada, entra no MODO INTERATIVO):"
    echo "  --source <fonte>  camara, senado, ou ambos"
    echo "  --limit <n>       Quantidade de registros por lote"
    echo "  --force           Força a execução mesmo se o banco já tiver dados"
    echo "  --years <anos>    Lista de anos separados por espaço (ex: \"2023 2024\")"
    echo "  --types <tipos>   Lista de tipos separados por espaço (ex: \"PL PEC\")"
    echo "  --help            Mostra esta mensagem"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --help) show_help; exit 0 ;;
        --source) SOURCE="$2"; shift 2 ;;
        --limit) LIMIT="$2"; shift 2 ;;
        --force) FORCE="--force"; shift 1 ;;
        --years) YEARS="$2"; shift 2 ;;
        --types) TYPES="$2"; shift 2 ;;
        *) log_error "Argumento inválido: $1"; show_help; exit 1 ;;
    esac
done

cd "$PROJECT_ROOT"

# Construção dinâmica de argumentos
ARGS=""
[ -n "$SOURCE" ] && ARGS="$ARGS --source $SOURCE"
[ -n "$LIMIT" ] && ARGS="$ARGS --limit $LIMIT"
[ -n "$FORCE" ] && ARGS="$ARGS $FORCE"
[ -n "$YEARS" ] && ARGS="$ARGS --years $YEARS"
[ -n "$TYPES" ] && ARGS="$ARGS --types $TYPES"

if [ -z "$ARGS" ]; then
    log_info "Iniciando Seed em MODO INTERATIVO..."
    # Sem -T para permitir entrada do usuário (TTY)
    docker compose exec backend uv run python src/seed.py
    log_success "Operação interativa finalizada."
    exit 0
fi

log_info "Executando seed automatizado..."
# shellcheck disable=SC2086
docker compose exec -T backend uv run python src/seed.py $ARGS

echo ""
echo "======================================================="
echo "       RELATÓRIO DE EXECUÇÃO (MODO AUTOMÁTICO)"
echo "======================================================="
echo " ✅ Status:          Finalizado"
echo " 📡 Fonte:           $SOURCE"
echo " 🔢 Limite/Lote:     ${LIMIT:-Padrão}"
[ -n "$YEARS" ] && echo " 📅 Anos:            $YEARS"
[ -n "$TYPES" ] && echo " 📑 Tipos:           $TYPES"
[ -n "$FORCE" ] && echo " ⚡ Forçado:         Sim" || echo " ⚡ Forçado:         Não"
echo "-------------------------------------------------------"
echo " Dica: Verifique os logs acima para o total de"
echo " itens inseridos e atualizados pela API."
echo "======================================================="
echo ""

log_success "Ambiente de dados atualizado com sucesso!"

