# Cheat Sheet do Projeto: Monitoramento de Tempo de Tramitação de Proposições

Guia rápido de comandos e fluxos. Atualize aqui sempre que surgir algo novo.

**Para contexto, veja [tech-stack.md](tech-stack.md) e [ARCHITECTURE.md](../ARCHITECTURE.md).**

---

## 1. Git

- `git status` → ver mudanças.
- `git add .` → adicionar tudo.
- `git commit -m "feat: nome-da-feature"` → commit imperativo.
- `git push` / `git pull` → sincronizar.
- `git checkout -b feat/nome-da-feature` → nova branch.

---

## 2. Docker / Docker Compose

- `docker-compose up -d` → subir PostgreSQL, Redis e backend [ADR-002, ADR-006].
- `docker-compose down` → desligar tudo.
- `docker-compose logs backend` → logs do FastAPI.
- `docker-compose exec backend bash` → terminal no container backend.
- `docker-compose exec postgres psql -U seu_usuario -d nome_banco` → conectar ao PostgreSQL.

---

## 3. FastAPI / Backend

- `uv run fastapi dev src/main.py` → rodar backend em modo dev [ADR-003].
- `uv run python src/seed.py` → popular banco com dados reais das APIs.
- `uv run python src/init_db.py` → criar tabelas no banco.
- Acessar [Swagger em `/docs`](http://localhost:8000/docs) para testar endpoints [ADR-003].

---

## 4. Testes — Backend

- `uv run pytest` → rodar todos os testes.
- `uv run pytest -m "not integration"` → apenas unitários.
- `uv run pytest -m "integration"` → apenas integração.
- `uv run ruff check .` → linting.

---

## 5. PostgreSQL

- `psql -h localhost -U seu_usuario -d nome_banco` → conectar localmente.
- `\dt` → listar tabelas.
- `\d+ nome_tabela` → detalhes da tabela [ADR-002].

---

## 6. Redis (planejado para R2)

- `redis-cli` → acessar Redis.
- `keys PROPOSICAO*` → ver chaves de cache [ADR-006].
- `FLUSHALL` → limpar cache (apenas em dev).

---

## 7. Frontend (React)

- `npm run dev` → dev server.
- `npm run build` → build produção.
- `npm run preview` → preview do build.
- `npm run lint` → verificar qualidade do código (ESLint).
- `npm run test` → rodar testes (Vitest).

---

**Links úteis:**

- [Tech Stack](tech-stack.md)
- [Arquitetura](../ARCHITECTURE.md)
- [ADRs](adr/)
- [README.md](../README.md)
