#!/usr/bin/env bash

# Script para instalar os Git Hooks do projeto Squad 13
# Garante que todos os desenvolvedores rodem a validação inteligente antes do push.

HOOK_PATH=".git/hooks/pre-push"

echo "🔧 Configurando Git Hooks..."

cat <<'EOF' > $HOOK_PATH
#!/usr/bin/env bash

# Cores para o terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛡️ Git Hook: Validação de Impacto (Rápida + Segura)...${NC}"

# Tenta identificar o branch remoto para comparar
BASE_REF=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "origin/develop")
CHANGED_FILES=$(git diff --name-only "$BASE_REF..HEAD")

# Flags de controle
RUN_BACKEND_UNIT=false
RUN_BACKEND_INTEGRATION=false
RUN_FRONTEND_RELATED=false
RUN_ALL=false

# Lista de arquivos para o Vitest
FRONTEND_FILES=""

for file in $CHANGED_FILES; do
  # Lógica Backend por Camadas (Segurança por vizinhança)
  if [[ $file == backend/src/domain/* ]] || [[ $file == backend/src/application/* ]]; then
    RUN_BACKEND_UNIT=true
  fi
  if [[ $file == backend/src/infrastructure/* ]] || [[ $file == backend/src/presentation/* ]]; then
    RUN_BACKEND_INTEGRATION=true
  fi
  
  # Lógica Frontend Related (Segurança via Grafo de Dependências)
  if [[ $file == frontend/* ]]; then
    if [[ $file == *.ts ]] || [[ $file == *.tsx ]] || [[ $file == *.js ]]; then
      RUN_FRONTEND_RELATED=true
      FRONTEND_FILES="$FRONTEND_FILES ${file#frontend/}"
    fi
  fi

  # Lógica Global
  if [[ $file == scripts/* ]] || [[ $file == "docker-compose.yml" ]] || [[ $file == "backend/alembic.ini" ]] || [[ $file == ".github/"* ]]; then
    RUN_ALL=true
  fi
done

EXIT_CODE=0

if [ "$RUN_ALL" = true ]; then
  echo -e "${BLUE}🔄 Mudança Crítica Detectada. Rodando Suite Completa...${NC}"
  ./scripts/ci/test.sh
  EXIT_CODE=$?
else
  if [ "$RUN_BACKEND_UNIT" = true ]; then
    echo -e "${BLUE}🐍 Mudanças em Domain/App. Rodando Testes Unitários...${NC}"
    cd backend && uv run pytest tests/unit && cd ..
    EXIT_CODE=$((EXIT_CODE + $?))
  fi
  if [ "$RUN_BACKEND_INTEGRATION" = true ]; then
    echo -e "${BLUE}🔌 Mudanças em Infra/Presentation. Rodando Testes de Integração...${NC}"
    cd backend && uv run pytest tests/integration && cd ..
    EXIT_CODE=$((EXIT_CODE + $?))
  fi
  if [ "$RUN_FRONTEND_RELATED" = true ]; then
    echo -e "${BLUE}⚛️ Rodando Testes de Impacto no Frontend (Vitest Related)...${NC}"
    cd frontend && npx vitest related $FRONTEND_FILES --run && cd ..
    EXIT_CODE=$((EXIT_CODE + $?))
  fi
fi

if [ $EXIT_CODE -ne 0 ]; then
  echo -e "${RED}❌ Falha na validação! O push foi bloqueado para sua segurança.${NC}"
  exit 1
fi

if [ "$RUN_BACKEND_UNIT" = false ] && [ "$RUN_BACKEND_INTEGRATION" = false ] && [ "$RUN_FRONTEND_RELATED" = false ] && [ "$RUN_ALL" = false ]; then
  echo -e "${GREEN}✅ Apenas documentação alterada. Push direto liberado!${NC}"
else
  echo -e "${GREEN}✅ Projeto íntegro! Validação seletiva concluída com sucesso.${NC}"
fi

exit 0
EOF

chmod +x $HOOK_PATH
echo "✅ Hook de pre-push instalado em $HOOK_PATH"
echo "💡 Agora suas mudanças serão validadas automaticamente antes de cada 'git push'."
