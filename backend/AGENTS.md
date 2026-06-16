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
