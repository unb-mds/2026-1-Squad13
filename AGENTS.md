# AGENTS.md - Diretrizes Operacionais e Constituição do Repositório

Este documento unifica e consolida o guia de contexto, regras inegociáveis e boas práticas para todos os agentes de Inteligência Artificial (incluindo Claude Code, Gemini, Antigravity, etc.) atuando no LexTrack.

## 1. Objetivo do Projeto
O **LexTrack** (Monitoramento de Tempo de Tramitação de Leis) é uma plataforma web para análise de eficiência do processo legislativo brasileiro (foco em PL e PEC). O sistema permite buscar proposições, acompanhar tramitações, identificar gargalos institucionais, visualizar métricas analíticas e previsões estatísticas de tempo de aprovação. Desenvolvido em contexto acadêmico, preza pelo equilíbrio entre funcionalidade real e boas práticas de engenharia de software.

## 2. Perfil Pedagógico
Como este é um projeto acadêmico, os agentes devem agir como mentores e seguir estas diretrizes ao interagir ou propor modificações:
*   **Explique o "Porquê":** Explique sempre a fundamentação conceitual, trade-offs de design e alternativas analisadas.
*   **Mudanças Incrementais:** Sempre analise, planeje (com aprovação) e depois implemente. Simplicidade deve prevalecer sobre complexidade prematura.
*   **Contexto de Código:** Nunca entregue blocos de código prontos sem o devido contexto e explicação das alterações feitas.

## 3. Regras Inegociáveis (Constituição)

### Arquitetura e Engenharia de Software
1.  **Layered Architecture:** O backend segue rigorosamente a estrutura em camadas: `presentation` → `application` → `domain` → `infrastructure`. Nenhuma camada pode acessar outra pulando níveis.
2.  **Domínio Isolado:** O domínio ([backend/src/domain/](file:///home/caio_martins/2026-1-Squad13/backend/src/domain/)) deve ser completamente puro e isolado de frameworks, banco de dados ou requisições HTTP. Dependências devem ser sempre invertidas (infraestrutura importa o domínio).
3.  **Ports & Adapters (Adapters & Repositories):** Toda integração externa (APIs da Câmara/Senado, banco de dados, cache) passa obrigatoriamente por interfaces declaradas como Ports na camada de `application`. As classes concretas ficam em `infrastructure`.
4.  **Resiliência:** Tratar dados incompletos ou corrompidos e falhas de APIs externas temporárias (Câmara/Senado) de forma elegante sem quebrar o sistema.
5.  **Frontend Feature-Based:** O frontend não deve conter regras de negócio complexas. Os componentes devem ser divididos por features ([frontend/src/features/](file:///home/caio_martins/2026-1-Squad13/frontend/src/features/)) e o layout por páginas ([frontend/src/pages/](file:///home/caio_martins/2026-1-Squad13/frontend/src/pages/)).

### Confiabilidade e Experiência do Usuário
6.  **Disponibilidade e Cache:** Não depender de chamadas em tempo real em fluxos críticos do usuário; prefira dados persistidos ou cacheados via Redis.
7.  **Estados de Interface:** Sempre forneça feedback visual para carregamento (`loading`), erros e ausência de dados (`empty states`), usando atributos ARIA apropriados.
8.  **Transparência e Previsão:** Previsões geradas por heurísticas/modelos preditivos devem exibir explicitamente que se tratam de estimativas estatísticas, sem garantias jurídicas. O disclaimer (`DISCLAIMER_IA`) deve estar sempre visível.

## 4. Stack Principal

*   **Backend:** [FastAPI](file:///home/caio_martins/2026-1-Squad13/backend/) + [SQLModel](https://sqlmodel.tiangolo.com) + [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes e virtualenv) + [Ruff](https://github.com/astral-sh/ruff) + [Pytest](https://docs.pytest.org).
    *   Estrutura de arquivos: [backend/src/](file:///home/caio_martins/2026-1-Squad13/backend/src/)
*   **Frontend:** [React 18](file:///home/caio_martins/2026-1-Squad13/frontend/) + [Vite](https://vitejs.dev) + [TypeScript](https://www.typescriptlang.org) + [Tailwind CSS 3](https://tailwindcss.com) + [Vitest](https://vitest.dev).
    *   Estrutura de arquivos: [frontend/src/](file:///home/caio_martins/2026-1-Squad13/frontend/src/)
*   **Banco de Dados & Cache:** [PostgreSQL](file:///home/caio_martins/2026-1-Squad13/docker-compose.yml) (migrações com Alembic via [scripts/db/migrate.sh](file:///home/caio_martins/2026-1-Squad13/scripts/db/migrate.sh)) + [Redis](file:///home/caio_martins/2026-1-Squad13/docker-compose.yml).
*   **Workers & Agendamento:** [Celery](file:///home/caio_martins/2026-1-Squad13/backend/src/infrastructure/workers/celery_app.py) + Celery Beat (Redis como Broker/Backend).
*   **Métricas de Desenvolvimento:** Squad Dashboard independente ([squad-dashboard/](file:///home/caio_martins/2026-1-Squad13/squad-dashboard/)).

## 5. Convenções Obrigatórias

*   **Prefixação de IDs:** Todo ID de proposição deve seguir o padrão `camara:<id>` ou `senado:<id>`. IDs sem prefixo são inválidos.
*   **Versionamento e Branches:**
    *   Nunca faça commits ou merges diretamente na branch `main`.
    *   Use o padrão de branches: `feat/<nome>`, `fix/<nome>`, `docs/<nome>`, `refactor/<nome>`.
*   **Mensagens de Commit (Conventional Commits):**
    *   Tipo em inglês (`feat`, `fix`, `chore`, `refactor`).
    *   Descrição em português no imperativo (ex: `feat: adiciona calculo de IAR`).
*   **Fluxo de Issues e Pull Requests:**
    *   Toda nova necessidade precisa de uma Issue associada.
    *   No merge de PRs na branch `develop`, as issues associadas devem ser marcadas com a label `status:done` e permanecer abertas. O fechamento definitivo (`Close`) ocorre somente quando integradas na `main`.
    *   Não realize merge sem CI/CD verde.

## 6. Rigor de Implementação (Anti-Erro)
Para garantir sucesso nas implementações de primeira tentativa ("First-Pass"), siga rigorosamente:
1.  **Inspecione antes de Instanciar:** Leia a assinatura do método `__init__` no arquivo de origem antes de usar fábricas ou instanciar serviços/repositórios. Nunca assuma nomes de parâmetros (ex: `repository` vs `repo`).
2.  **Integridade de Novos Módulos:** Ao criar um arquivo, garanta que todos os tipos e imports necessários estejam presentes. Execute `ruff check <arquivo>` imediatamente após criar ou editar arquivos Python.
3.  **Validação de Dependências:** Ao realizar tarefas interdependentes, releia os arquivos modificados para atualizar seu mapa da estrutura, em vez de confiar apenas no histórico de chat.

## 7. Funcionalidades Descontinuadas
*   **Autenticação (JWT):** O sistema de autenticação e proteção de rotas foi descontinuado e completamente removido no PR #197. Não reimplementar fluxos de login, cadastro, logout ou recuperação de senha.

## 8. Ferramentas e Configurações Específicas dos Agentes
*   **Claude Code / Agentes de Terminal:** Não executam `git commit`, `git push` ou criação de PR de forma automática (a menos que explicitamente solicitado pelo usuário). Ao finalizar as tarefas, devem exibir o path da worktree ativa, a branch atual, o resultado do `git status`, o diff final e os comandos recomendados para execução manual do desenvolvedor.

## 9. Skills e Plugins de Infraestrutura
O repositório disponibiliza ferramentas de governança e validação de compliance sob a forma de `Skills` (ver pasta [.agents/skills/](file:///home/caio_martins/2026-1-Squad13/.agents/skills/)):
*   `architecture-compliance-checker` para validar limites arquiteturais.
*   `db-migration-governor` para monitoramento de models e migrations SQLModel.
*   `test-coverage-enforcer` para verificar cobertura de testes.
*   `frontend-governance` para validações de UX e tokens Tailwind.

## 10. O Que Evitar
*   Respostas genéricas ou superficiais.
*   Introdução de novas dependências sem justificativa clara.
*   Refatorações em larga escala sem um MVP funcional testável.
*   Abstrações enterprise prematuras.
