#!/bin/bash

# Falhar imediatamente em caso de erro, variável não definida ou erro em pipe
set -euo pipefail

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

# 2. Obter IP externo da VM
GCP_IP="${GCP_IP:-}"
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

# 3. Verificar arquivo .env na raiz
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env não encontrado na raiz. Criando a partir do .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ .env criado na raiz.${NC}"
    else
        echo -e "${RED}❌ Erro: .env.example não encontrado.${NC}"
        exit 1
    fi
fi

# Ajustar VITE_API_URL e ALLOWED_ORIGINS no .env para o IP da GCP
sed -i "s|VITE_API_URL=.*|VITE_API_URL=http://${GCP_IP}:8000|g" .env
sed -i "s|ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=http://${GCP_IP}:5173|g" .env

# 4. Subir Ambiente (Tudo de uma vez - Healthchecks cuidam da ordem)
echo -e "${YELLOW}⚙️  Subindo containers (build e infra)...${NC}"
# Adicionamos --profile worker para garantir que o Celery suba no GCP
docker compose ${COMPOSE_FILES} --profile worker up -d --build

# 5. Polling para garantir que a API está pronta
echo -e "${BLUE}⏳ Aguardando backend responder (healthcheck)...${NC}"
MAX_RETRIES=30
COUNT=0
until $(curl -sSf http://localhost:8000/health > /dev/null 2>&1) || [ $COUNT -eq $MAX_RETRIES ]; do
    printf "."
    sleep 2
    ((COUNT++))
done

if [ $COUNT -eq $MAX_RETRIES ]; then
    echo -e "\n${RED}❌ Erro: Backend não subiu a tempo.${NC}"
    docker compose ${COMPOSE_FILES} logs backend
    exit 1
fi
echo -e "\n${GREEN}✅ Backend online!${NC}"

# 6. Inicializar e Popular banco
echo -e "${YELLOW}🗄️  Inicializando tabelas e semeando dados...${NC}"
docker compose ${COMPOSE_FILES} exec -T backend uv run python src/init_db.py
docker compose ${COMPOSE_FILES} exec -T backend uv run python src/seed.py

# 7. Status final
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
