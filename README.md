# 2026-1-Squad13
## Arquitetura

Para entender como o sistema é estruturado, as decisões técnicas
tomadas e o que cada membro do time precisa estudar, leia o
[ARCHITECTURE.md](./ARCHITECTURE.md).

## ADRs — Architecture Decision Records

| ID | Decisão | Status |
|----|---------|--------|
| [ADR-001](./docs/adr/ADR-001-layered-architecture.md) | Layered Architecture como padrão arquitetural | Proposta |
| [ADR-002](./docs/adr/ADR-002-postgresql.md) | PostgreSQL como banco de dados | Proposta |
| [ADR-003](./docs/adr/ADR-003-fastapi.md) | FastAPI como framework do backend | Proposta |
| [ADR-004](./docs/adr/ADR-004-batch-coleta.md) | Batch diário como estratégia de coleta | Proposta |
| [ADR-005](./docs/adr/ADR-005-adapter-pattern.md) | Padrão Adapter para isolamento das APIs externas | Proposta |
| [ADR-006](./docs/adr/ADR-006-redis-cache.md) | Redis para cache de respostas | Proposta |