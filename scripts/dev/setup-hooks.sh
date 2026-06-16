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

# Listas de arquivos para validações incrementais
FRONTEND_FILES=""
BACKEND_FILES=""
for file in $CHANGED_FILES; do
  if [[ $file == backend/* ]] && [[ $file == *.py ]]; then
    BACKEND_FILES="$BACKEND_FILES ${file#backend/}"
  fi
  if [[ $file == backend/src/domain/* ]] || [[ $file == backend/src/application/* ]]; then
    RUN_BACKEND_UNIT=true
  fi
  if [[ $file == backend/src/infrastructure/* ]] || [[ $file == backend/src/presentation/* ]]; then
    RUN_BACKEND_INTEGRATION=true
  fi
  
  # Lógica Frontend Related (Segurança via Grafo de Dependências) e Linter
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
  # --- VALIDAÇÕES DE LINTER & ESTILO INCREMENTAIS ---
  
  # Linter Backend (Ruff)
  if [ -n "$BACKEND_FILES" ]; then
    echo -e "${BLUE}🐍 Verificando Linter e Formatação no Backend (Incremental)...${NC}"
    cd backend
    uv run ruff check $BACKEND_FILES
    RUFF_CHECK_CODE=$?
    uv run ruff format --check $BACKEND_FILES
    RUFF_FORMAT_CODE=$?
    cd ..
    if [ $RUFF_CHECK_CODE -ne 0 ] || [ $RUFF_FORMAT_CODE -ne 0 ]; then
      echo -e "${RED}❌ Falha de linter/formatação no Backend!${NC}"
      echo -e "${RED}Execute 'uv run ruff check --fix .' e 'uv run ruff format .' na pasta backend/ para corrigir.${NC}"
      EXIT_CODE=$((EXIT_CODE + 1))
    fi
  fi

  # Linter Frontend (ESLint)
  if [ -n "$FRONTEND_FILES" ]; then
    echo -e "${BLUE}⚛️ Verificando Linter no Frontend (Incremental)...${NC}"
    cd frontend
    npx eslint $FRONTEND_FILES
    ESLINT_CODE=$?
    cd ..
    if [ $ESLINT_CODE -ne 0 ]; then
      echo -e "${RED}❌ Falha de linter no Frontend! Corrija os erros acima antes de dar push.${NC}"
      EXIT_CODE=$((EXIT_CODE + 1))
    fi
  fi

  # Se houver erros de linter, aborta imediatamente antes de rodar os testes
  if [ $EXIT_CODE -ne 0 ]; then
    echo -e "${RED}❌ Validação de linter falhou. Abortando execução dos testes.${NC}"
    echo -e "${RED}❌ Falha na validação! O push foi bloqueado para sua segurança.${NC}"
    exit 1
  fi

  # --- SUÍTES DE TESTE SELETIVAS ---
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
