# 2026-1-Squad13

## Visão geral

Sistema para busca e acompanhamento de proposições legislativas, com foco inicial em PL e PEC, permitindo consulta por filtros como tipo, número, ano, autor, UF do autor e status de tramitação.

## Como rodar o projeto completo

Para testar a integração entre o frontend e o backend, você precisará de dois terminais abertos simultaneamente.

### 1. Rodando o Backend

```bash
cd backend
uv sync
uv run fastapi dev src/main.py
```
O backend rodará em: http://localhost:8000

### 2. Rodando o Frontend

Em um novo terminal:

```bash
cd frontend
npm install
npm run dev
```
O frontend rodará em: http://localhost:5173

---

## Integração Backend-Frontend

O sistema está configurado para que o frontend consuma dados reais do backend. 

- **CORS:** O backend está configurado para aceitar requisições do `localhost:5173`.
- **Normalização:** Usamos Schemas Pydantic no backend com `alias_generator` para converter campos `snake_case` (Python) em `camelCase` (JSON/TypeScript) automaticamente.
- **Mapeamento:** O arquivo `frontend/src/shared/lib/api.ts` contém as chamadas de API que conectam os filtros da interface aos endpoints do FastAPI.

## Estrutura do repositório

```text
/
├── backend/
├── frontend/
├── docs/
└── README.md
```

## Como rodar o backend localmente

### Pré-requisitos

- Python 3.12+
- uv instalado

### Passos

```bash
cd backend
uv sync
uv run fastapi dev src/main.py
```

A aplicação ficará disponível localmente em uma URL como:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

### Rodando os testes

Os testes estão divididos em unitários e de integração (marcados com `integration`).

```bash
cd backend
# Rodar apenas testes unitários (rápidos)
uv run pytest -m "not integration"

# Rodar testes de integração (podem chamar APIs externas)
uv run pytest -m "integration"

# Rodar todos os testes
uv run pytest
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

## Estado atual

- **Backend:** FastAPI com Layered Architecture, adaptadores reais para as APIs da Câmara e do Senado, integração com PostgreSQL via SQLAlchemy, e testes automatizados (unitários e de integração) configurados com pytest.
- **Frontend:** React + TypeScript + Vite integrado ao backend, com ESLint configurado e build validado automaticamente no CI.
- **CI/CD:** GitHub Actions com workflows separados para frontend e backend, disparados automaticamente em PRs para `main`.

Para contribuir, consulte o [CONTRIBUTING.md](./CONTRIBUTING.md).
