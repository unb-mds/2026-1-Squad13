# AGENTS.md - Diretrizes do Backend

Este guia orienta agentes de IA atuando na pasta `backend/` do LexTrack.

## 1. Arquitetura (Layered Architecture)
O backend segue estritamente a divisão em camadas: `presentation` → `application` → `domain` → `infrastructure`.
* **Regra de ouro:** Nenhuma camada interna pode importar uma camada mais externa.
* **Isolamento do Domínio:** O domínio ([backend/src/domain/](file:///home/caio/2026-1-Squad13/backend/src/domain/)) deve ser Python puro, sem imports de frameworks (como FastAPI) ou adapters.
* **Ports & Adapters:** Toda integração externa passa obrigatoriamente por interfaces declaradas como Ports na camada de `application`. As implementações concretas residem em `infrastructure`.

## 2. Comandos e Scripts de Teste/Lint
Evite comandos Python avulsos. Utilize a suíte de scripts da raiz:
* **Validação Completa (CI Local):** Rodar `./scripts/ci/backend.sh` a partir da raiz do repositório.
  * *O que faz:* Roda `ruff check`, `ruff format --check`, compilação estática do `main.py` e os testes do `pytest` (excluindo testes de integração externa).
* **Executar Linter e Formatter manualmente:**
  * `uv run ruff check .`
  * `uv run ruff format .`
* **Testes unitários/integração:**
  * Rodar testes de unidade locais: `uv run pytest` (a partir de `backend/`)
  * Rodar testes de integração externa (Câmara/Senado): `uv run pytest -m integration`
* **Migrations de Banco de Dados:**
  * Aplicar migrações locais: `./scripts/db/migrate.sh`
  * Inicializar tabelas: `./scripts/db/init.sh`

## 3. Definition of Done (DoD Local)
1. Executar `./scripts/ci/backend.sh` e obter sucesso (zero erros).
2. Garantir conformidade de camadas executando a verificação de imports (`.agents/skills/architecture-compliance-checker/scripts/verify-layers.sh`).
3. Adicionar testes relevantes na pasta `backend/tests/` para validar novas lógicas ou correções de bugs.
4. Qualquer alteração em tabelas ou models deve ser acompanhada de uma migração Alembic gerada e testada.

---

## 4. Inspeção Dinâmica de Endpoints (Fatos Dinâmicos)
Não mantenha listas estáticas de rotas/endpoints na documentação em markdown, pois elas tornam-se obsoletas rapidamente. Em vez disso, utilize os seguintes métodos para inspecioná-los dinamicamente:
1. **Documentação OpenAPI (Swagger UI):** Com o backend rodando localmente, acesse a interface interativa em `http://localhost:8000/docs`.
2. **Terminal (CLI Command):** A partir da pasta `backend/`, execute o comando abaixo para listar em tempo real todas as rotas registradas e seus respectivos métodos HTTP:
   ```bash
   uv run python -c "from src.main import app; [print(f'{list(r.methods)[0] if r.methods else \"GET\"} {r.path}') for r in app.routes]"
   ```

## 5. Scheduler de Produção (GitHub Actions Cron)
Em produção, os agendamentos diários são controlados por workflows do GitHub Actions que acionam rotas internas do backend (protegidas por cabeçalho `X-Internal-Token`). 

| Horário BRT | Workflow GitHub Actions | Rota Acionada | Descrição |
|---|---|---|---|
| **02h37** | `cron-coleta.yml` | `POST /internal/tarefas/coleta` | Coleta em lote das proposições na Câmara e Senado. |
| **03h00** | `cron-baselines.yml` | `POST /internal/tarefas/baselines` | Recálculo das medianas históricas (baselines) por grupo/fase. |
| **04h00** | `cron-metricas.yml` | `POST /internal/tarefas/metricas` | Cálculo de IAR, IAF, IEI e status de atraso para proposições ativas. |

*Nota: Para desenvolvimento local, as rotas equivalentes são configuradas no schedule do Celery Beat via Docker Compose.*
