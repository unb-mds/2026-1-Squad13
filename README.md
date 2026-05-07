# 2026-1-Squad13

## Visão geral

Sistema para busca e acompanhamento de proposições legislativas, com foco inicial em PL e PEC, permitindo consulta por filtros como tipo, número, ano, autor, UF do autor e status de tramitação.

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
| [ADR-001](./docs/adr/ADR-001-layered-architecture.md) | Layered Architecture como padrão arquitetural    | Proposta |
| [ADR-002](./docs/adr/ADR-002-postgresql.md)           | PostgreSQL como banco de dados                   | Proposta |
| [ADR-003](./docs/adr/ADR-003-fastapi.md)              | FastAPI como framework do backend                | Proposta |
| [ADR-004](./docs/adr/ADR-004-batch-coleta.md)         | Batch diário como estratégia de coleta           | Proposta |
| [ADR-005](./docs/adr/ADR-005-adapter-pattern.md)      | Padrão Adapter para isolamento das APIs externas | Proposta |
| [ADR-006](./docs/adr/ADR-006-redis-cache.md)          | Redis para cache de respostas                    | Proposta |

## Estado atual

Atualmente o projeto possui a estrutura inicial do backend, configuração de testes automatizados (unitários e de integração) e a primeira configuração local com FastAPI. O frontend e as integrações externas ainda estão em construção.
egrações externas ainda estão em construção.
