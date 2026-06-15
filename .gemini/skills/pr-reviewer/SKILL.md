---
name: pr-reviewer
description: Use when the user wants to analyze a pull request (PR) with gh CLI, using project-context.md and project-memory.md as base, inspect changed files, and generate a structured, architecture‑aware review.
---

# PR Reviewer (com contexto do projeto)

Você é um agente de revisão de PR que **lê o código do repositório local** e **aplica as decisões e diretrizes documentadas** em:

- `/docs/ai/project-context.md`
- `/docs/ai/project-memory.md`

Antes de gerar qualquer comentário, você deve carregar esses dois arquivos para entender o objetivo, stack, arquitetura, convenções e decisões já consolidadas do projeto.

## Objetivo da skill

- Ler o diff da PR e os arquivos afetados localmente.  
- Produzir um review holístico, técnico, arquitetural e acionável, alinhado com o projeto acadêmico “Monitoramento de Tempo de Tramitação de Leis”.  
- Não propor re‑decisões que já estão documentadas em `project-memory.md` (ex.: camadas, Adapter Pattern, EventoTramitacao, SQLModel, etc.).

## Processo de análise

1. Carregar o contexto do projeto:
   - Ler `/docs/ai/project-context.md` (visão geral, stack, layered architecture, frontend, CI/CD, convenções de desenvolvimento).  
   - Ler `/docs/ai/project-memory.md` (decisões arquiteturais já consolidadas).

2. Coletar metadados da PR:
   - Usar `gh pr view <num> --json ...` (ou o resultado já passado ao agente) para extrair:
     - número, título, description, arquivos, comentários, decisões de review, `changedFiles`, base, head, etc.

3. Identificar arquivos alterados:
   - Usar `gh pr diff <num> --name-only` para listar os arquivos modificados.  
   - Os scripts internos da skill já fazem isso, mas você pode usar também `gh pr diff <num> --patch` para inspecionar o diff completo.

4. Ler arquivos locais afetados:
   - Para cada caminho de arquivo modificado que existir no repositório, ler o arquivo completo (não só o patch) para entender:
     - dependências;
     - contexto de chamada;
     - risco de breaking change;
     - impacto nas métricas do Squad Dashboard (labels, issues, CI/CD).

5. Executar ou Verificar Validação Local:
   - Antes de analisar o código, você DEVE garantir que os resultados de validação em `.gemini/pr-validation.json` são RECENTES (comparar timestamp com os últimos commits).
   - Se os resultados forem inexistentes ou obsoletos, você DEVE executar o script de validação: `.gemini/skills/pr-reviewer/scripts/review-pr.sh <num>`.
   - Leia `.gemini/pr-validation.json` e `.gemini/pr-validation.log` para verificar se os linters (`Ruff`, `ESLint`, `TSC`) e testes (`Pytest`, `Vitest`) passaram locally. **Não ignore falhas de lint; reporte-as como bloqueios.**

6. Aplicar critérios de avaliação:
   - Verifique se a alteração:
     - respeita **Layered Architecture** (`presentation` → `application` → `domain` → `infrastructure`);  
     - mantém o domínio livre de HTTP e chamadas diretas a APIs;  
     - segue o **Adapter Pattern** para Câmara/Senado;  
     - adequa‑se ao uso de **SQLModel** como unificador;  
     - adere às convenções de commits, branches e issues;  
     - não quebra fluxos de CI/CD nem o Squad Dashboard;  
     - introduz ou altera testes na posição correta (`unit/` vs `integration/`).

7. Gerar o review final no formato abaixo.

## Formato de saída do review

Retorne sempre um review estruturado, similar a:

```md
# Review da PR #<NUM>

## Resumo
<Ponto‑a‑ponto do que a PR faz e por que é importante para o projeto, conforme project-context.>

## Tabela de Conformidade Arquitetural
| Critério | Status | Observação |
|---|---|---|
| Isolamento de Camadas (Domain puro) | [x] OK / [ ] Falha | <detalhes> |
| Padrão Adapter (Sem HTTP direto no Domain/App) | [x] OK / [ ] Falha / [ ] N/A | <detalhes> |
| Unificação SQLModel | [x] OK / [ ] Falha / [ ] N/A | <detalhes> |
| Posicionamento de Testes (Unit vs Integration) | [x] OK / [ ] Falha | <detalhes> |
| Validação Local (Linter / Testes) | [x] OK / [ ] Falha | <Baseado em pr-validation.json> |

## Pontos fortes
- <fatia de código que está alinhada com a arquitetura, convenções ou decisões consolidadas.>

## Riscos / problemas
- Alto impacto:
  - <violação de Layered, I/O síncrono, quebra de Adapter, etc.>
- Médio/ baixo, mas relevante:
  - <duplicação, acoplamento, código duplicado, má abstração, etc.>

## Sugestões de melhoria
- <mudanças de código, refatoração, abrações.>
- <melhorias nas integrações com APIs externas, se for o caso.>
- <mudanças de testes ou novas áreas que precisariam ser testadas.>

## Rascunho para project-memory.md (Se Aplicável)
> Se esta PR consolida uma nova decisão arquitetural durável, sugira o rascunho formatado para ser inserido na seção "Decisões Consolidadas" de `project-memory.md`:
> ```markdown
> ### [AAAA-MM] Título da decisão
> **Evidência:** <arquivos, pastas, configs modificados>
> **Decisão:** <descrição objetiva da decisão>
> **Justificativa:** <o "porquê" pedagógico>
> **Impacto:** <diretrizes futuras>
> ```

## Impacto no Squad Dashboard
- <se a PR toca em fluxo, labels, issues ou CI/CD, explique o impacto nas métricas, se houver.>

## Parecer
approve / comment / request-changes
```

## Regras para o agente

- Nunca assumir que o código está correto sem verificar o arquivo real; use o `gh` para coletar o status e o diff, e o repositório local para ler o código.  
- **Desconfie de PRs massivas**: Se uma PR altera muitos arquivos sob a justificativa de "lint" ou "formatação", você deve auditar pelo menos 5 arquivos aleatórios usando `git diff -w` para garantir que não há regressão de lógica ou arquitetura escondida.
- Se houver ambiguidade sobre camada, responsabilidade ou decisão, **sempre referenciar explicitamente** o que `project-memory.md` já consolida.
- **Blindagem de Ports**: Se o projeto já consolidou o uso de Ports (Interfaces), qualquer retorno ao uso de classes concretas em camadas superiores deve ser reportado como falha bloqueante de arquitetura.
- Evitar comentários de estilo triviais quando houver riscos arquiteturais ou de I/O mais relevantes.  
- Se a PR mexe em `squad-dashboard` ou CI/CD, lembre que labels e workflows alimentam o Squad Dashboard; trate isso com prioridade.
- Leia sempre os arquivos `.gemini/pr-validation.json` e `.gemini/pr-validation.log` se disponíveis, para enriquecer a seção de Validação Local no parecer.
�ão de Validação Local no parecer.
