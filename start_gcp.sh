#!/bin/bash

# Cores para o output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

COMPOSE_FILES="-f docker-compose.yml -f docker-compose.gcp.yml"

echo -e "${BLUE}☁️  Iniciando Ambiente GCP — Monitor Legislativo...${NC}\n"

# 1. Verificar Docker
if ! docker --version > /dev/null 2>&1; then
    echo -e "${RED}❌ Erro: Docker não encontrado. Verifique a instalação.${NC}"
    exit 1
fi

if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ Erro: Sem permissão para acessar o Docker.${NC}"
    echo -e "${YELLOW}Dica: sudo usermod -aG docker \$USER && newgrp docker${NC}"
    exit 1
fi

# 2. Obter IP externo da VM
if [ -z "${GCP_IP}" ]; then
    echo -e "${YELLOW}Qual é o IP externo da VM GCP? (ex: 34.x.x.x)${NC}"
    read -r GCP_IP
fi

if [ -z "${GCP_IP}" ]; then
    echo -e "${RED}❌ Erro: IP externo não informado. Abortando.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ IP externo: ${GCP_IP}${NC}\n"
export GCP_IP

# 3. Verificar arquivo .env do backend
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  backend/.env não encontrado. Criando a partir do .env.example...${NC}"
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo -e "${GREEN}✅ backend/.env criado. Revise as senhas antes de continuar em ambientes expostos.${NC}"
    else
        echo -e "${RED}❌ Erro: backend/.env.example não encontrado.${NC}"
        exit 1
    fi
fi

# 4. Subir infraestrutura
echo -e "${YELLOW}🐘 Subindo banco de dados e cache...${NC}"
docker compose ${COMPOSE_FILES} up -d db redis

echo -e "${BLUE}⏳ Aguardando serviços de infraestrutura estabilizarem...${NC}"
sleep 5

# 5. Subir aplicações
echo -e "${YELLOW}⚙️  Subindo backend e frontend (com rebuild)...${NC}"
docker compose ${COMPOSE_FILES} up -d --build backend frontend

# 6. Verificar backend
echo -e "${BLUE}⏳ Verificando saúde do backend...${NC}"
sleep 5
if ! docker ps | grep -q monitor_backend; then
    echo -e "${RED}❌ Erro: container do backend não está rodando.${NC}"
    echo -e "${YELLOW}Logs:${NC}"
    docker logs monitor_backend
    exit 1
fi

# 7. Inicializar banco
echo -e "${YELLOW}🗄️  Inicializando tabelas do banco de dados...${NC}"
docker compose ${COMPOSE_FILES} exec -T backend uv run python src/init_db.py

# 8. Popular banco
echo -e "${YELLOW}🌱 Populando banco com dados reais (seed)...${NC}"
docker compose ${COMPOSE_FILES} exec -T backend uv run python src/seed.py

# 9. Status final
echo -e "\n${BLUE}📊 Status dos containers:${NC}"
docker compose ${COMPOSE_FILES} ps

echo -e "\n${GREEN}✨ AMBIENTE GCP PRONTO! ✨${NC}"
echo -e "--------------------------------------"
echo -e "🌐 Frontend: http://${GCP_IP}:5173"
echo -e "📡 Backend:  http://${GCP_IP}:8000"
echo -e "🏥 Health:   http://${GCP_IP}:8000/health"
echo -e "📖 API docs: http://${GCP_IP}:8000/docs"
echo -e "--------------------------------------"
echo -e "${YELLOW}Dica: docker compose ${COMPOSE_FILES} logs -f${NC}\n"
