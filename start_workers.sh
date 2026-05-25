#!/bin/bash

# Cores para o output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}👷 Iniciando Workers Celery (Worker & Beat)...${NC}"

# Sobe apenas os containers do perfil 'worker'
docker compose up -d --profile worker celery_worker celery_beat

echo -e "${GREEN}✅ Workers inicializados em background!${NC}"
echo -e "${YELLOW}Dica: Use 'docker compose logs -f celery_worker' para monitorar as tarefas.${NC}"
