# Deploy em VM GCP — Ambiente de Homologação

> Este guia cobre o setup completo para executar o projeto em uma VM Ubuntu na GCP via Docker Compose.
> Não inclui HTTPS, domínio próprio, Nginx, Terraform, Kubernetes ou configuração de produção enterprise-grade.

---

## Pré-requisitos

- VM Ubuntu 22.04 LTS na GCP (mínimo recomendado: `e2-standard-2`, 2 vCPUs, 8 GB RAM)
- IP externo estático associado à VM
- Acesso SSH à VM
- Docker e Docker Compose instalados na VM
- Git instalado na VM
- Portas abertas no firewall GCP:

| Porta | Serviço       | Expor        |
|-------|---------------|--------------|
| 22    | SSH           | Sim          |
| 5173  | Frontend Vite | Sim          |
| 8000  | Backend API   | Sim          |
| 5432  | PostgreSQL    | **Não**      |
| 6379  | Redis         | **Não**      |

Via `gcloud`:

```bash
gcloud compute firewall-rules create allow-ssh \
  --allow tcp:22 --target-tags=<sua-vm-tag>

gcloud compute firewall-rules create allow-frontend \
  --allow tcp:5173 --target-tags=<sua-vm-tag>

gcloud compute firewall-rules create allow-backend \
  --allow tcp:8000 --target-tags=<sua-vm-tag>
```

---

## Instalar Docker na VM

Se Docker não estiver instalado:

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

## Checklist de primeiro deploy (setup inicial)

Execute estes passos **na ordem exata** ao configurar a VM pela primeira vez.

### 1. Clonar o repositório

```bash
git clone https://github.com/unb-mds/2026-1-Squad13.git
cd 2026-1-Squad13
```

### 2. Criar o `.env` a partir do exemplo — OBRIGATÓRIO

```bash
cp .env.example .env
```

> **Nunca suba o ambiente sem este passo.** O `docker-compose.yml` lê variáveis exclusivamente do `.env` na raiz. Sem ele, todos os containers falharão na inicialização.

### 3. Editar o `.env` com os valores reais

```bash
nano .env
```

Substitua os placeholders pelos valores reais da VM. Consulte a tabela de [Variáveis críticas](#variáveis-críticas) para saber o que cada variável controla e o impacto de configurá-la errado.

Valores obrigatórios a alterar:

```dotenv
# Banco de dados — POSTGRES_HOST deve ser 'db', nunca 'localhost'
POSTGRES_PASSWORD=senha-segura-aqui
POSTGRES_HOST=db

# pgAdmin — use domínio válido, não .local
PGADMIN_DEFAULT_EMAIL=dev@projeto.com
PGADMIN_DEFAULT_PASSWORD=senha-pgadmin-aqui

# Autenticação — gere uma chave aleatória segura
SECRET_KEY=chave-secreta-longa-e-aleatoria

# URLs com o IP externo real da VM
VITE_API_URL=http://IP_EXTERNO:8000
ALLOWED_ORIGINS=http://IP_EXTERNO:5173
```

### 4. Subir o ambiente

```bash
docker compose up -d --build
```

### 5. Verificar que todos os containers estão `Up`

```bash
docker compose ps
```

Esperado: todos os serviços com status `Up` (ou `Up (healthy)` para `db`).

### 6. Verificar que o backend está saudável

```bash
curl http://IP_EXTERNO:8000/health
```

Resposta esperada:

```json
{"status": "ok", "database": "connected"}
```

---

## Atualizações subsequentes (CD automático)

Após o primeiro setup, **todo push para `develop`** que altere arquivos em `backend/`, `frontend/`, `docker-compose.yml` ou `.env.example` dispara o deploy automático via GitHub Actions.

O CD executa na VM:

```bash
git pull origin develop
./start_gcp.sh
```

> **O `.env` nunca é sobrescrito pelo CD.** Ele é criado manualmente no primeiro setup e permanece na VM. Se precisar alterar variáveis, edite o `.env` diretamente na VM e reinicie os containers afetados.

Se precisar redeployar manualmente, utilize o script de automação que já lida com healthchecks e workers:

```bash
./start_gcp.sh
```

```bash
cd 2026-1-Squad13
git pull origin develop
docker compose up -d --build
```

---

## Variáveis críticas

| Variável                | Valor esperado na VM          | Impacto se errado                                        |
|-------------------------|-------------------------------|----------------------------------------------------------|
| `POSTGRES_HOST`         | `db`                          | Backend não conecta ao banco → 500 em todas as rotas     |
| `POSTGRES_PASSWORD`     | senha real (não placeholder)  | Banco recusa conexão → 500 em todas as rotas             |
| `SECRET_KEY`            | string longa e aleatória      | JWT inválido → falha no login e autenticação             |
| `VITE_API_URL`          | `http://IP_EXTERNO:8000`      | Frontend não alcança a API → NetworkError no navegador   |
| `ALLOWED_ORIGINS`       | `http://IP_EXTERNO:5173`      | CORS bloqueado → requisições do frontend rejeitadas      |
| `PGADMIN_DEFAULT_EMAIL` | email com domínio válido (.com) | Container pgadmin entra em loop de restart             |
| `REDIS_HOST`            | `redis`                       | Cache e Celery falham → tarefas assíncronas quebram      |

---

## Acesso no navegador

| Serviço    | URL                            |
|------------|--------------------------------|
| Frontend   | `http://IP_EXTERNO:5173`       |
| Backend    | `http://IP_EXTERNO:8000`       |
| API docs   | `http://IP_EXTERNO:8000/docs`  |

---

## pgAdmin (opcional)

O pgAdmin sobe junto com `docker compose up`. Para acessá-lo, abra temporariamente a porta 8080 no firewall GCP e acesse `http://IP_EXTERNO:8080`.

> Feche a porta 8080 após o uso — não deixe pgAdmin exposto publicamente.

Para parar somente o pgAdmin:

```bash
docker compose stop pgadmin
```

---

## Parar o ambiente

```bash
docker compose down
```

Para remover também os volumes (apaga dados do banco):

```bash
docker compose down -v
```

---

## Troubleshooting

| Erro | Causa provável | Solução |
|------|----------------|---------|
| `500 Internal Server Error` no login ou em qualquer rota | `POSTGRES_HOST=localhost` no `.env`, ou variáveis ausentes (`.env` nunca foi criado a partir do `.env.example`) | Verificar se `.env` existe na raiz; garantir `POSTGRES_HOST=db`; reiniciar backend: `docker compose restart backend` |
| `CORS Missing Allow Origin` | `ALLOWED_ORIGINS` não configurado ou com IP errado | Adicionar `ALLOWED_ORIGINS=http://IP_EXTERNO:5173` no `.env`; reiniciar backend: `docker compose restart backend` |
| `NetworkError` no frontend ao chamar a API | `VITE_API_URL=http://localhost:8000` no `.env` | Atualizar `VITE_API_URL=http://IP_EXTERNO:8000` no `.env`; rebuild do frontend: `docker compose up -d --build frontend` |
| Container `pgadmin` em `Restarting` em loop | `PGADMIN_DEFAULT_EMAIL` com domínio `.local` inválido | Trocar para email com domínio válido (ex: `dev@projeto.com`) no `.env`; recriar: `docker compose up -d pgadmin` |
| CD falhou com `i/o timeout` na conexão SSH | Porta 22 bloqueada no firewall GCP | Criar regra de firewall liberando TCP 22 para `0.0.0.0/0` no Console GCP |
| CD falhou com `no key found` ou `invalid format` | `GCP_SSH_KEY` configurado em formato PPK (PuTTY) em vez de OpenSSH | Exportar a chave privada em formato OpenSSH via PuTTYgen → Conversions → Export OpenSSH key |
| Backend sobe mas banco não conecta (`database: disconnected`) | Container `db` ainda inicializando quando backend tentou conectar | Aguardar alguns segundos e verificar novamente: `curl http://IP_EXTERNO:8000/health` |
| `docker compose up` falha com `permission denied` | Usuário não está no grupo `docker` | Executar `sudo usermod -aG docker $USER && newgrp docker` e repetir o comando |

---

## Observações

- Este ambiente usa `fastapi dev` e `npm run dev` — adequado para desenvolvimento/homologação, não para produção.
- PostgreSQL e Redis não expõem portas públicas; ficam acessíveis apenas entre containers.
- O `.env` na VM nunca é versionado e nunca é sobrescrito pelo CD. Guarde os valores em local seguro.
- Para produção, use proxy reverso (Nginx/Caddy) e certificados TLS.
