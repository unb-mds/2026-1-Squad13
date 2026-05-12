#!/bin/bash

# Cores para o output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando Validação Completa do Projeto...${NC}\n"

# 1. Testes do Backend
echo -e "${BLUE}--- [BACKEND] Executando Pytest ---${NC}"
cd backend
export PYTHONPATH=src
uv run pytest
BACKEND_EXIT=$?
cd ..

if [ $BACKEND_EXIT -ne 0 ]; then
    echo -e "\n${RED}❌ Falha nos testes do Backend. Abortando...${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Backend aprovado!${NC}\n"

# 2. Testes do Frontend
echo -e "${BLUE}--- [FRONTEND] Executando Vitest ---${NC}"
cd frontend
npm run test -- --run
FRONTEND_EXIT=$?
cd ..

if [ $FRONTEND_EXIT -ne 0 ]; then
    echo -e "\n${RED}❌ Falha nos testes do Frontend. Abortando...${NC}"
    exit 1
fi

echo -e "\n${GREEN}✨ PROJETO VALIDADO COM SUCESSO! ✨${NC}"
exit 0
