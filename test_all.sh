#!/bin/bash

# Cores para o output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando Validação Blindada do Projeto...${NC}\n"

# --- [BACKEND] ---
echo -e "${BLUE}--- [BACKEND] Verificando Integridade e Testes ---${NC}"
cd backend
export PYTHONPATH=src

# 1. Check de Sintaxe/Lint (Rápido)
echo -e "${YELLOW}🔍 Rodando Ruff (Linter)...${NC}"
uv run ruff check .
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Falha na qualidade do código Backend (Lint).${NC}"
    exit 1
fi

# 2. Testes Unitários e Integração
echo -e "${YELLOW}🧪 Rodando Pytest...${NC}"
uv run pytest
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Falha nos testes do Backend.${NC}"
    exit 1
fi
cd ..
echo -e "${GREEN}✅ Backend aprovado!${NC}\n"


# --- [FRONTEND] ---
echo -e "${BLUE}--- [FRONTEND] Verificando Integridade e Testes ---${NC}"
cd frontend

# 1. Check de Tipos e Imports (Pega erros de 'No matching export')
echo -e "${YELLOW}🔍 Verificando integridade de tipos (TSC)...${NC}"
# Usamos npx tsc para verificar sem gerar arquivos de saída
npx tsc --noEmit
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro de integridade/tipagem no Frontend. Verifique imports e exports.${NC}"
    exit 1
fi

# 2. Lint (Qualidade)
echo -e "${YELLOW}🎨 Rodando ESLint...${NC}"
npm run lint
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Falha na qualidade do código Frontend (Lint).${NC}"
    exit 1
fi

# 3. Testes
echo -e "${YELLOW}🧪 Rodando Vitest...${NC}"
npm run test -- --run
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Falha nos testes do Frontend.${NC}"
    exit 1
fi
cd ..

echo -e "\n${GREEN}✨ PROJETO 100% VALIDADO E ÍNTEGRO! ✨${NC}"
exit 0
