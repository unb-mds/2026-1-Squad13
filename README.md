# 2026-1-Squad13

## Visão geral

Sistema para busca e acompanhamento de proposições legislativas, com foco inicial em PL e PEC, permitindo consulta por filtros como tipo, número, ano, autor, UF do autor e status de tramitação.

---

## ⚡ Modo Rápido (Recomendado)

Se você possui **Docker** e **uv** instalados, utilize os scripts de automação na raiz do projeto:

### 1. Subir o Ambiente Completo (Docker)
Este comando sobe o Banco (PostgreSQL), Cache (Redis), Backend e Frontend automaticamente.
```bash
./start_dev.sh
```
- **Frontend:** http://localhost:5173
- **Backend:** http://localhost:8000
- **Docs (Swagger):** http://localhost:8000/docs

### 2. Rodar Todos os Testes e Validações
Executa linting, checagem de tipos e todos os testes (Unitários e Integração) de ambos os apps.
```bash
./test_all.sh
```

---

## 🛠️ Como rodar manualmente

Caso prefira rodar os serviços separadamente para desenvolvimento:

### 1. Rodando o Backend (API)

```bash
cd backend
uv sync
uv run fastapi dev src/main.py
```
O backend rodará em: http://localhost:8000

### 2. Rodando o Frontend (Aplicação Principal)

```bash
cd frontend
npm install
npm run dev
```
O frontend rodará em: http://localhost:5173

### 3. Rodando o Squad Dashboard (Gestão)

```bash
cd squad-dashboard
npm install
npm run dev
```
O dashboard de métricas do time rodará em: http://localhost:5174

---

## 📊 Gestão e Governança

O projeto utiliza um **Squad Dashboard** automatizado para monitorar a saúde do desenvolvimento em tempo real.

- **Métricas Reais**: Burndown, Velocity e Progresso de Features são extraídos diretamente da API do GitHub.
- **Integração de CI**: O dashboard exibe o percentual de cobertura de código real medido nos pipelines de Pull Request.
- **Transparência**: Dados de contribuição (commits/tasks) por membro são atualizados a cada push na `main`.

Para mais detalhes sobre como a automação funciona, consulte o [AUTOMATION.md](./squad-dashboard/AUTOMATION.md).

---

## 🧪 Testes Automatizados

Além do `./test_all.sh`, você pode rodar testes específicos:

### Backend (Pytest)
```bash
cd backend
# Apenas unitários
uv run pytest -m "not integration"
# Apenas integração
uv run pytest -m "integration"
```

### Frontend (Vitest)
```bash
cd frontend
npm run test
```

## 🏗️ Integração Backend-Frontend

O sistema está configurado para que o frontend consuma dados reais do backend via PostgreSQL. 

- **CORS:** O backend está configurado para aceitar requisições do `localhost:5173`.
- **Persistência:** O backend utiliza `SQLModel` para persistência em banco de dados real.
- **Normalização:** Usamos Schemas Pydantic no backend para converter campos `snake_case` (Python) em `camelCase` (JSON/TypeScript) automaticamente.
- **Mapeamento:** O arquivo `frontend/src/shared/lib/api.ts` contém as chamadas de API que conectam a interface aos endpoints do FastAPI.

## Estrutura do repositório

```text
/
├── backend/            ← API FastAPI com SQLModel
├── frontend/           ← Aplicação React + Vite (Principal)
├── squad-dashboard/    ← Painel de métricas e gestão do time
├── docs/               ← Documentação técnica e ADRs
└── README.md
```

## Arquitetura

Para entender como o sistema é estruturado, as decisões técnicas tomadas e o que cada membro do time precisa estudar, leia o [ARCHITECTURE.md](./ARCHITECTURE.md).

## ADRs — Architecture Decision Records

| ID                                                    | Decisão                                          | Status   |
| ----------------------------------------------------- | ------------------------------------------------ | -------- |
| [ADR-001](./docs/adr/ADR-001-layered-architecture.md) | Layered Architecture como padrão arquitetural    | Aceita   |
| [ADR-002](./docs/adr/ADR-002-postgresql.md)           | PostgreSQL como banco de dados                   | Aceita   |
| [ADR-003](./docs/adr/ADR-003-fastapi.md)              | FastAPI como framework do backend                | Aceita   |
| [ADR-004](./docs/adr/ADR-004-batch-coleta.md)         | Batch diário como estratégia de coleta           | Aceita   |
| [ADR-005](./docs/adr/ADR-005-adapter-pattern.md)      | Padrão Adapter para isolamento das APIs externas | Aceita   |
| [ADR-006](./docs/adr/ADR-006-redis-cache.md)          | Redis para cache de respostas                    | Aceita   |
| [ADR-007](./docs/adr/ADR-007-testing-strategy.md)     | Estratégia de Testes (Frontend e Backend)        | Aceita   |
| [ADR-008](./docs/adr/ADR-008-github-actions-data-pipeline.md) | Pipeline de Dados para o Squad Dashboard | Aceita   |
| [ADR-009](./docs/adr/ADR-009-squad-dashboard-ghpages.md)      | Squad Dashboard no GitHub Pages          | Aceita   |

## Estado atual

- **Backend:** FastAPI com Layered Architecture, modelo analítico `EventoTramitacao` com classificação de eventos e fases legislativas, autenticação JWT (`/auth/login`, `/auth/register`), adaptadores reais para as APIs da Câmara e do Senado, integração com PostgreSQL via SQLModel, e testes automatizados (unitários e de integração) com pytest.
- **Frontend:** React + TypeScript + Vite integrado ao backend real, com ESLint configurado e build validado automaticamente no CI. Dashboard com métricas de fluxo e gráfico de burnup semântico.
- **CI/CD:** GitHub Actions com workflows separados para frontend, backend e squad-dashboard, disparados automaticamente em PRs para `main` e `develop`.

Para contribuir, consulte o [CONTRIBUTING.md](./CONTRIBUTING.md).
