#!/bin/bash

# Cores para o output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando Ambiente de Desenvolvimento Legislativo...${NC}\n"

# 1. Verificar se o Docker está instalado
if ! docker --version > /dev/null 2>&1; then
    echo -e "${RED}❌ Erro: O comando 'docker' não foi encontrado. Verifique a instalação.${NC}"
    exit 1
fi

# 2. Verificar permissão do Docker
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ Erro: Sem permissão para acessar o Docker.${NC}"
    echo -e "${YELLOW}Dica: Tente rodar com 'sudo' ou adicione seu usuário ao grupo 'docker':${NC}"
    echo -e "      sudo usermod -aG docker \$USER && newgrp docker"
    exit 1
fi

# 3. Verificar arquivo .env
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo backend/.env não encontrado. Criando a partir do .env.example...${NC}"
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo -e "${GREEN}✅ backend/.env criado com sucesso!${NC}"
    else
        echo -e "${RED}❌ Erro: backend/.env.example não encontrado para criar o .env.${NC}"
        exit 1
    fi
fi

# 4. Subir a infraestrutura (Banco e Cache) primeiro
echo -e "${YELLOW}🐘 Subindo Banco de Dados e Cache...${NC}"
docker compose up -d db redis

# Aguardar um pouco para o banco estabilizar
echo -e "${BLUE}⏳ Aguardando serviços de infra estabilizarem...${NC}"
sleep 5

# 3. Subir as aplicações
echo -e "${YELLOW}⚙️  Subindo Backend e Frontend...${NC}"
docker compose up -d backend frontend

# 4. Verificar status
echo -e "\n${BLUE}📊 Status dos Containers:${NC}"
docker compose ps

echo -e "\n${GREEN}✨ AMBIENTE PRONTO PARA USO! ✨${NC}"
echo -e "--------------------------------------"
echo -e "🌐 Frontend: http://localhost:5173"
echo -e "📡 Backend:  http://localhost:8000"
echo -e "🏥 Health:   http://localhost:8000/health"
echo -e "--------------------------------------"
echo -e "${YELLOW}Dica: Use 'docker compose logs -f' para ver os logs em tempo real.${NC}\n"
