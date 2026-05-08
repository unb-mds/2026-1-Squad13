# Tech Stack: Monitoramento de Tempo de Tramitação de Proposições

Resumo das tecnologias principais usadas no projeto, explicando **o que é** e **por que escolhemos essa tecnologia**, ligando tudo aos [ADRs](docs/adr/) e à [arquitetura definida em `ARCHITECTURE.md`](ARCHITECTURE.md).

---

## 1. Stack geral

- **Backend:** Python + FastAPI + SQLAlchemy + Pydantic
- **Frontend:** React + Vite
- **Banco de dados:** [PostgreSQL](docs/adr/ADR-002-postgresql.md) (Planejado/Mock em memória no momento)
- **Cache + Celery broker:** [Redis](docs/adr/ADR-006-redis-cache.md) (Planejado)
- **Worker & agendamento:** Celery + Celery Beat (Planejado)
- **Contêineres:** Docker Compose
- **CI/CD:** GitHub Actions

---

## 2. Backend: Python + FastAPI

- **O que é:** FastAPI é um framework web para construir APIs REST com Python, com suporte a `async/await` e integração com Pydantic para validação e documentação automática.
- **Por que usamos:** [ADR-003: FastAPI](docs/adr/ADR-003-fastapi.md)
  - Permite trabalho assíncrono com as APIs da Câmara e do Senado.
  - Gera documentação OpenAPI/Swagger automaticamente em `/docs`.
- **Camada na arquitetura:** Apresentação (`src/presentation/controllers/`).

---

## 3. Pydantic

- **O que é:** biblioteca de validação e serialização de dados, baseada em tipos Python.
- **Por que usamos:**
  - Valida automaticamente `request` e `response` [ADR-003: FastAPI](docs/adr/ADR-003-fastapi.md).
  - Usado nos adapters para normalizar respostas das APIs [ADR-005: Adapter Pattern](docs/adr/ADR-005-adapter-pattern.md).
- **Onde aparece:** schemas de entrada/saída nos controllers e adapters.

---

## 4. PostgreSQL

- **O que é:** banco de dados relacional robusto, com suporte a `WINDOW FUNCTIONS` e SQL avançado.
- **Por que usamos:** [ADR-002: PostgreSQL](docs/adr/ADR-002-postgresql.md)
  - Permite calcular métricas temporais diretamente em SQL.
  - Suporta SQLAlchemy com interface assíncrona.
- **Estado atual:** O sistema utiliza um **Mock em memória** (`ProposicaoRepository`) para facilitar o desenvolvimento inicial. O PostgreSQL será integrado na próxima fase.
- **Camada na arquitetura:** Infraestrutura (`src/infrastructure/repositories/`).

---

## 5. Redis

- **O que é:** banco de dados em memória, usado como cache e broker de mensagens.
- **Por que usamos:** [ADR-006: Redis Cache](docs/adr/ADR-006-redis-cache.md)
  - Cache de respostas pesadas para consultas rápidas.
  - Broker do Celery para o worker de coleta [ADR-004: Batch Coleta](docs/adr/ADR-004-batch-coleta.md).
- **Camada na arquitetura:** Infraestrutura (`src/infrastructure/cache/`).

---

## 6. Celery + Celery Beat

- **O que é:** biblioteca de tarefas de background agendadas.
- **Por que usamos:** [ADR-004: Batch diário](docs/adr/ADR-004-batch-coleta.md)
  - Executa coleta das APIs da Câmara/Senado em batch diário às 02h.
- **Camada na arquitetura:** Infraestrutura (`src/infrastructure/workers/`).

---

## 7. Padrão Adapter

- **O que é:** padrão de design para isolar APIs externas.
- **Por que usamos:** [ADR-005: Adapter Pattern](docs/adr/ADR-005-adapter-pattern.md)
  - `CamaraAdapter` e `SenadoAdapter` convertem formatos diferentes para entidade `Proposicao`.
- **Camada na arquitetura:** Infraestrutura (`src/infrastructure/adapters/`).

---

## 8. Docker Compose

- **O que é:** ferramenta para orquestrar múltiplos containers.
- **Por que usamos:**
  - Roda PostgreSQL, Redis, backend e worker com um comando só.
- **Configuração:** `docker-compose.yml` na raiz.

---

## 9. GitHub Actions

- **O que é:** CI/CD integrado ao GitHub.
- **Por que usamos:**
  - Testes automáticos a cada push.
- **Configuração:** `.github/workflows/`.

---

Veja também:

- [Arquitetura completa](ARCHITECTURE.md)
- [Cheat Sheet de comandos](docs/cheat-sheet.md)
- [README.md](README.md).
