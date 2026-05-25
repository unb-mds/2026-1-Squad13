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

# 3. Verificar arquivo .env na raiz
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado na raiz. Criando a partir do .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ .env criado com sucesso na raiz!${NC}"
    else
        echo -e "${RED}❌ Erro: .env.example não encontrado para criar o .env.${NC}"
        exit 1
    fi
fi

# 4. Subir toda a infraestrutura e aplicações
echo -e "${YELLOW}⚙️  Iniciando todos os serviços (Banco, Cache, Backend, Frontend, Workers)...${NC}"
echo -e "${BLUE}Nota: O Docker Compose aguardará os healthchecks para garantir que tudo esteja pronto.${NC}"
# Adicionamos --profile worker para incluir o Celery por padrão no dev local
docker compose --profile worker up -d --build --wait

# 5. Popular o Banco com Dados Reais (Variados) se necessário
echo -e "${YELLOW}🌱 Verificando necessidade de popular o banco (Seed)...${NC}"
echo -e "${BLUE}Nota: O script detecta automaticamente se o banco já possui dados.${NC}"
# Passamos argumentos para evitar o menu interativo e agilizar o processo inicial
docker compose exec -T backend uv run python src/seed.py --source camara --limit 3

# 6. Verificar status final
echo -e "\n${BLUE}📊 Status dos Containers:${NC}"
docker compose ps

echo -e "\n${GREEN}✨ AMBIENTE PRONTO PARA USO! ✨${NC}"
echo -e "--------------------------------------"
echo -e "🌐 Frontend: http://localhost:5173"
echo -e "📡 Backend:  http://localhost:8000"
echo -e "🏥 Health:   http://localhost:8000/health"
echo -e "--------------------------------------"
echo -e "${YELLOW}Dica: Use 'docker compose logs -f' para ver os logs em tempo real.${NC}\n"
