# AGENTS.md - Diretrizes Operacionais do LexTrack

Este documento é a fonte única de verdade para todos os agentes de Inteligência Artificial atuando no LexTrack.

## 1. Visão Geral e Modo de Atuação
* **Objetivo:** O **LexTrack** monitora tempos de tramitação de proposições (PL e PEC) no Congresso para identificar gargalos e prever a eficiência legislativa.
* **Modo Pedagógico:** Como projeto acadêmico, aja como mentor:
  - **Porquê:** Explique os trade-offs de design e escolhas conceituais.
  - **Incremental:** Planeje antes de alterar; priorize simplicidade.
  - **Contexto:** Nunca envie código isolado sem explicar a motivação e as dependências envolvidas.

## 2. Regras Globais Inegociáveis
1. **Padrão de IDs:** Todo ID de proposição deve seguir obrigatoriamente o padrão `camara:<id>` ou `senado:<id>`. IDs sem prefixo são inválidos.
2. **JWT Descontinuado:** Não recrie fluxos de login/autenticação. O sistema é público (removido no PR #197).
3. **Transparência de Estimativas:** Toda previsão gerada por modelos preditivos deve vir acompanhada do disclaimer (`DISCLAIMER_IA`) visível, indicando se tratar de previsão estatística sem valor jurídico.
4. **Links Relativos Obrigatórios:** É expressamente proibido o uso de caminhos absolutos do sistema local (ex: `file:///home/` ou `/home/usuario/`) em qualquer arquivo de documentação. Todos os links internos para pastas ou arquivos do repositório devem usar links markdown relativos (ex: `[texto](./caminho/do/arquivo.md)`).
5. **Análise e Validação Prévia Obrigatória:** O agente de IA não deve realizar alterações de código, refatorações, correções ou criação de novos arquivos sem antes apresentar um planejamento ou análise prévia ao desenvolvedor. O início de qualquer modificação física na árvore de trabalho (`working tree`) do repositório está estritamente condicionado à validação e autorização explícita do usuário para o plano proposto.

## 3. Fluxo de Versionamento e Commits
* **Criação de Branches:** Sempre sugira/crie uma nova branch a partir de `develop` para cada foco de implementação (`feat/<nome>`, `fix/<nome>`, `docs/<nome>`, `refactor/<nome>`).
* **Commits Dinâmicos e Atômicos:** Se o usuário solicitar a realização de commits, execute-os diretamente. Divida as alterações em commits atômicos (focados e auto-contidos), com mensagens em inglês (tipo) e descrição em português (descrição imperativa). Ex: `feat: adiciona calculo de IAR`.
* **Push sob Solicitação:** Se o usuário solicitar a realização do `git push`, execute-o diretamente. 
* **Validação Pre-Push Hook:** O repositório conta com um hook de validação inteligente no push (configurado por `./scripts/dev/setup-hooks.sh`, localizado em `.git/hooks/pre-push`). Esse hook roda testes e linters incrementais de forma automática antes que o envio ao repositório remoto seja concluído.
* **Fluxo de Integração:** 
  - Feature branch -> merge em `develop` (via PR).
  - Periodicamente, um PR de release consolida a `develop` estável na `main`.

## 4. Ciclo de Vida de Issues e PRs (Conforme Skills)
* **Keyword em PRs:** Em Pull Requests para `develop`, use `Ref #XYZ` ou `Related #XYZ`. Nunca use palavras-chave de fechamento automático (`Closes #XYZ`, `Fixes #XYZ`) para evitar fechamento prematuro.
* **Transições de Status das Issues:**
  - **PR Aberto:** Transicionar para `status:review`.
  - **Merge na `develop`:** Alterar para `status:done` (manter a issue aberta).
  - **Merge na `main`:** Fechar (**Close**) a issue definitivamente.

## 5. Scripts Utilitários (Evite Comandos Avulsos)
Sempre prefira usar os scripts centrais do repositório para evitar duplicação de contexto e garantir alinhamento com a Integração Contínua (CI):
* **Rodar Validação Completa (Linter + Testes):** `./scripts/ci/test.sh` (Script principal que aciona os testes do backend e frontend).
* **Subir infraestrutura de Dev:** `./scripts/dev/up.sh` (Use com `--no-workers` caso não precise do Celery).
* **Derrubar infraestrutura de Dev:** `./scripts/dev/down.sh`
* **Aplicar Migrações de BD:** `./scripts/db/migrate.sh`
* **Inicializar Banco vazio:** `./scripts/db/init.sh`
* **Iniciar Workers de fila:** `./scripts/dev/workers.sh`
* **Popular Banco de Dados:** `./scripts/dev/seed.sh`

## 6. Definition of Done (DoD)
Antes de declarar qualquer tarefa concluída, o agente deve garantir:
1. Executar o script `./scripts/ci/test.sh` localmente e obter sucesso absoluto (zero erros).
2. Não violar limites de acoplamento das camadas do backend.
3. Prover testes unitários e de integração relevantes na pasta do módulo alterado.
4. Validar se a modificação necessita de migração de banco de dados e gerá-la de forma correta.

## 7. Guias Operacionais Locais (Delegados)
As diretrizes e comandos específicos de cada área estão localizadas em seus respectivos subdiretórios:
* **Backend (Camadas, SQLModel, FastAPI):** [backend/AGENTS.md](./backend/AGENTS.md)
* **Frontend (React, Componentes, UX/ARIA):** [frontend/AGENTS.md](./frontend/AGENTS.md)
* **Squad Dashboard (Métricas de Desenvolvimento):** [squad-dashboard/AGENTS.md](./squad-dashboard/AGENTS.md)

## 8. Skills de Infraestrutura (Gatilhos de Uso)
Utilize as skills disponíveis na pasta `.agents/skills/` conforme o contexto da tarefa:
* [architecture-compliance-checker](./.agents/skills/architecture-compliance-checker/SKILL.md) -> Use ao editar/criar arquivos no backend para checar regras de importação.
* [db-migration-governor](./.agents/skills/db-migration-governor/SKILL.md) -> Use quando models do SQLModel forem modificados para auditar esquemas e migrations.
* [test-coverage-enforcer](./.agents/skills/test-coverage-enforcer/SKILL.md) -> Use para validar se novas features do backend possuem cobertura mínima de testes.
* [frontend-governance](./.agents/skills/frontend-governance/SKILL.md) -> Use para validação de componentes visuais, conformidade de design tokens e UX.
* [pr-manager](./.agents/skills/pr-manager/SKILL.md) / [github-issue-governor](./.agents/skills/github-issue-governor/SKILL.md) -> Use para gestão e compliance no fluxo de PRs e issues.

## 9. Links de Referência
* [README.md](./README.md)
* [ARCHITECTURE.md](./ARCHITECTURE.md)
* [tech-stack.md](./docs/tech-stack.md)
