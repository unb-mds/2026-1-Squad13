# Deploy em VM GCP — Ambiente Remoto de Desenvolvimento/Homologação

> Este guia cobre apenas o setup mínimo para executar o projeto em uma VM Ubuntu na GCP via Docker Compose.
> Não inclui HTTPS, domínio próprio, Nginx, Terraform, Kubernetes ou configuração de produção enterprise-grade.

---

## Pré-requisitos

- VM Ubuntu 22.04 LTS na GCP (mínimo recomendado: `e2-standard-2`, 2 vCPUs, 8 GB RAM)
- IP externo estático associado à VM
- Acesso SSH à VM
- Git instalado na VM

---

## 1. Configurar firewall na GCP

No Console GCP ou via `gcloud`, abra as portas necessárias:

| Porta | Serviço       | Expor |
|-------|---------------|-------|
| 22    | SSH           | Sim   |
| 5173  | Frontend Vite | Sim   |
| 8000  | Backend API   | Sim   |
| 5432  | PostgreSQL    | **Não** |
| 6379  | Redis         | **Não** |

Via `gcloud`:

```bash
gcloud compute firewall-rules create allow-frontend \
  --allow tcp:5173 --target-tags=<sua-vm-tag>

gcloud compute firewall-rules create allow-backend \
  --allow tcp:8000 --target-tags=<sua-vm-tag>
```

---

## 2. Instalar Docker na VM

```bash
# Conecte na VM via SSH
ssh usuario@IP_EXTERNO

# Instala Docker
curl -fsSL https://get.docker.com | sudo sh

# Adiciona seu usuário ao grupo docker (evita uso de sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verifica instalação
docker --version
docker compose version
```

---

## 3. Clonar o repositório

```bash
git clone https://github.com/<org>/2026-1-Squad13.git
cd 2026-1-Squad13
```

---

## 4. Criar arquivos de ambiente (`.env`)

### Backend (`backend/.env`)
Copie o exemplo e ajuste os valores:

```bash
cp backend/.env.example backend/.env
```

Edite `backend/.env` e configure ao menos:

```dotenv
POSTGRES_DB=monitor_db
POSTGRES_USER=app_user
POSTGRES_PASSWORD=<senha-segura>
POSTGRES_HOST=db
POSTGRES_PORT=5432

PGADMIN_DEFAULT_EMAIL=dev@projeto.local
PGADMIN_DEFAULT_PASSWORD=<senha-pgadmin>

# Substitua IP_EXTERNO pelo IP público da sua VM GCP
ALLOWED_ORIGINS=http://IP_EXTERNO:5173
```

### Raiz (`.env`)
Crie um arquivo `.env` na raiz do projeto para configurar o endereço da API que o Frontend (Vite) irá consumir:

```bash
# Substitua IP_EXTERNO pelo IP público da sua VM GCP
echo "VITE_API_URL=http://IP_EXTERNO:8000" > .env
```

> `ALLOWED_ORIGINS` também pode ser passado pelo override GCP (o `start_gcp.sh` faz isso automaticamente).
> Ao usar o script, você pode deixar esta variável sem o IP externo no `.env` e ela será sobrescrita.

---

## 5. Subir o ambiente

### Opção A — via script (recomendado)

```bash
chmod +x start_gcp.sh
./start_gcp.sh
```

O script pedirá o IP externo da VM e subirá tudo com o override GCP.

### Opção B — manualmente

```bash
export GCP_IP=IP_EXTERNO

# Inicializa infra
docker compose -f docker-compose.yml -f docker-compose.gcp.yml up -d db redis

# Aguarda estabilizar
sleep 5

# Sobe aplicações com rebuild
docker compose -f docker-compose.yml -f docker-compose.gcp.yml up -d --build backend frontend

# Inicializa banco e seed
docker compose exec -T backend uv run python src/init_db.py
docker compose exec -T backend uv run python src/seed.py
```

---

## 6. Verificar saúde

```bash
# Containers em execução
docker compose ps

# Healthcheck da API
curl http://IP_EXTERNO:8000/health

# Logs em tempo real
docker compose logs -f
```

Resposta esperada do healthcheck:

```json
{"status": "ok", "database": "connected"}
```

---

## 7. Acessar no navegador

| Serviço  | URL                          |
|----------|------------------------------|
| Frontend | `http://IP_EXTERNO:5173`     |
| Backend  | `http://IP_EXTERNO:8000`     |
| API docs | `http://IP_EXTERNO:8000/docs`|

---

## 8. pgAdmin (opcional)

O pgAdmin não é exposto por padrão no perfil GCP. Para subir somente quando necessário:

```bash
export GCP_IP=IP_EXTERNO
docker compose -f docker-compose.yml -f docker-compose.gcp.yml --profile pgadmin up -d pgadmin
```

Acesse em `http://IP_EXTERNO:8080`.

> Atenção: se ativar o pgAdmin, abra temporariamente a porta 8080 no firewall GCP e feche após o uso.

---

## 9. Parar o ambiente

```bash
docker compose -f docker-compose.yml -f docker-compose.gcp.yml down
```

Para remover também os volumes (apaga dados do banco):

```bash
docker compose -f docker-compose.yml -f docker-compose.gcp.yml down -v
```

---

## Observações

- Este ambiente usa `fastapi dev` e `npm run dev` — adequado para desenvolvimento/homologação, não para produção.
- PostgreSQL e Redis ficam acessíveis apenas entre containers (sem porta pública).
- Não configure HTTPS neste setup; para produção, use um proxy reverso (Nginx/Caddy) e certificados TLS adequados.
