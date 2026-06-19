---
name: pr-manager
description: Use when the user wants to create, configure, or review/analyze a pull request (PR) using gh CLI, ensuring compliance with branch conventions, issues mapping, active status label transitions, lifecycle rules, and physical validation.
---

# PR Manager (com contexto de governança e revisão)

Você é um agente de gerenciamento e revisão de PRs que **lê o código do repositório local**, **aplica as decisões e diretrizes de governança** e **automatiza a criação e a validação** dos Pull Requests.

Antes de qualquer ação, carregue as diretrizes documentadas em:
- `/AGENTS.md`
- `/ARCHITECTURE.md`

## Objetivo da skill

- **Criação de PRs:** Automatizar a criação de Pull Requests no GitHub seguindo rigorosamente a governança de associação de issues, ciclo de vida de labels da branch de destino e descrição robusta do PR.
- **Revisão de PRs:** Analisar o diff e os arquivos afetados localmente para produzir um review holístico, técnico, arquitetural e acionável.
- Não propor re‑decisões que já estão documentadas em `ARCHITECTURE.md` ou `AGENTS.md` (ex.: camadas, Adapter Pattern, EventoTramitacao, SQLModel, etc.).

## Processo de criação de PRs

Ao ser solicitado a criar um Pull Request, você deve seguir o seguinte protocolo obrigatório:

1. **Identificar a Branch de Destino:**
   - A branch padrão para novas funcionalidades é a `develop` (onde a nota de ciclo de vida é necessária). A branch `main` é reservada para integrações finais.

2. **Mapeamento e Associação de Issues (Rastreabilidade):**
   - Liste os commits da branch atual em relação à branch de destino para entender as modificações:
     `git log <destino>..HEAD --oneline`
   - Liste as issues abertas no repositório:
     `gh issue list --limit 100`
   - Identifique quais issues foram resolvidas ou afetadas pelas modificações.
   - Adicione referências explícitas a essas issues na descrição do PR usando o formato `Ref #XYZ` (se o destino for `develop`) ou `Resolve #XYZ` (se o destino for `main`).

3. **Validação Local Física:**
   - Garanta que todos os testes e linters estejam passando localmente antes do push. Se houver falhas, corrija-as.
   - Capture o log final de aprovação dos testes locais para servir de evidência na descrição do PR.

4. **Transição de Status das Labels no GitHub:**
   - Para toda issue associada ao PR, atualize seu rótulo no GitHub adicionando a label `status:review` (e removendo `status:in_progress` ou `status:todo` se existirem):
     `gh issue edit <num_issue> --add-label "status:review" --remove-label "status:in_progress" --remove-label "status:todo"`

5. **Construção do Body do PR (Padrão PR #267):**
   - Crie uma descrição estruturada, rica e dividida categoricamente contendo:
     - **Resumo Executivo:** Um sumário rápido e claro sobre o impacto das alterações no ecossistema do LexTrack.
     - **Nota de Status de Ciclo de Vida:** (Apenas se o destino for `develop`) Um alerta informando que as issues associadas devem passar para `status:done` no merge na `develop`, mas permanecer abertas até a integração em `main`.
     - **Modificações Categorizadas:** Tópicos agrupados com emojis de acordo com a área modificada (ex: `🛡️ Resiliência & Integração`, `⚙️ Engenharia & Infraestrutura`, `🧪 Testes & Validação`).
     - **Evidência de Validação Física:** O log resumido dos testes locais que comprova a estabilidade do código.
     - **Issues Relacionadas:** Lista das issues mapeadas com o prefixo de rastreabilidade adequado.

6. **Publicar e Criar o PR:**
   - Faça o push da branch para o repositório remoto: `git push origin <branch>`
   - Crie o PR de forma não interativa usando a CLI do GitHub:
     `gh pr create --title "<tipo>: <descricao_em_portugues>" --body-file <caminho_do_body_file> --base <destino>`

## Processo de análise de PRs (Revisão)

1. Carregar o contexto do projeto:
   - Ler `/AGENTS.md` (visão geral, perfil pedagógico, regras inegociáveis, stack, convenções).  
   - Ler `/ARCHITECTURE.md` (layered architecture, ports & adapters, ADRs, estado atual).

2. Coletar metadados da PR (e status de mergeability/conflitos):
   - Usar `gh pr view <num> --json ...` (ou o resultado já passado ao agente) para extrair:
     - número, título, descrição, arquivos, comentários, decisões de review, `changedFiles`, base, head, `mergeable` (para detectar conflitos com a branch de destino), etc.

3. Identificar arquivos alterados:
   - Para otimizar a velocidade e economizar requisições de rede da API do GitHub, prefira listar os arquivos modificados usando o comando git local: `git diff origin/main...HEAD --name-only`. 
   - Se necessário, você também pode usar `gh pr diff <num> --patch` para inspecionar o patch completo.

4. Ler arquivos locais afetados:
   - Para cada caminho de arquivo modificado que existir no repositório, ler o arquivo completo (não só o patch) para entender:
     - dependências;
     - contexto de chamada;
     - risco de breaking change;
     - impacto nas métricas do Squad Dashboard (labels, issues, CI/CD).

5. Executar ou Verificar Validação Local:
   - Antes de analisar o código, você DEVE garantir que os resultados de validação em `.agents/scratch/pr-validation.json` são RECENTES (comparar timestamp com os últimos commits).
   - Se os resultados forem inexistentes ou obsoletos, execute a validação local usando a ferramenta de comandos do Antigravity (`pytest`, `npm run lint` ou o script `.agents/skills/pr-manager/scripts/review-pr.sh <num>`).
   - Leia `.agents/scratch/pr-validation.json` e `.agents/scratch/pr-validation.log` para verificar se os linters (`Ruff`, `ESLint`, `TSC`) e testes (`Pytest`, `Vitest`) passaram locally. **Não ignore falhas de lint; reporte-as como bloqueios.**
   - **Auto-remediação de Lints:** Caso a validação local acuse erros triviais de estilo ou formatação (ex: problemas que o `ruff --fix` resolveria), utilize as ferramentas de edição de arquivos do Antigravity para aplicar os patches e correções diretamente na branch de trabalho local antes de finalizar o parecer.

6. Aplicar critérios de avaliação:
   - Verifique se a alteração:
     - respeita **Layered Architecture** (`presentation` → `application` → `domain` → `infrastructure`);  
     - mantém o domínio livre de HTTP e chamadas diretas a APIs;  
     - segue o **Adapter Pattern** para Câmara/Senado;  
     - adequa‑se ao uso de **SQLModel** como unificador;  
     - adere às convenções de commits, branches e issues;
     - não quebra fluxos de CI/CD nem o Squad Dashboard;
     - introduz ou altera testes na posição correta (`unit/` vs `integration/`).
   - Verifique a **Qualidade da Descrição e Governança do PR**:
     - Avalie se a descrição (body) do PR no GitHub está robusta seguindo o padrão do **PR #267**:
       - Contém resumo executivo claro sobre o impacto no ecossistema.
       - Lista as issues associadas (`Ref #` ou `Resolve #`).
       - Caso o destino seja a branch `develop`, exige a nota de status de ciclo de vida (`> [!NOTE] Nota de Status`) explicando que as issues vinculadas devem ser movidas para `status:done` no board, mas permanecerem abertas até a fusão em `main`.
       - Divide as modificações categorizadas tematicamente com emojis (ex: `🛡️ Resiliência & Integração`, `⚙️ Engenharia & Infraestrutura`, `📚 Governança & Organização`).
       - Documenta evidências de validação física (como logs de teste locais ou contagens de registros inseridos no banco local pós-seeding).

7. Gerar o review final no formato abaixo. Salve este parecer estruturado como um artefato do Antigravity CLI (com metadados `UserFacing: true`) no diretório da conversa para visualização elegante pelo desenvolvedor.

## Formato de saída do review

Retorne sempre um review estruturado, similar a:

```md
# Review da PR #<NUM>

## Resumo
<Ponto‑a‑ponto do que a PR faz e por que é importante para o projeto, conforme AGENTS.md e ARCHITECTURE.md.>

## Tabela de Conformidade Arquitetural
| Critério | Status | Observação |
|---|---|---|
| Isolamento de Camadas (Domain puro) | [x] OK / [ ] Falha | <detalhes> |
| Padrão Adapter (Sem HTTP direto no Domain/App) | [x] OK / [ ] Falha / [ ] N/A | <detalhes> |
| Unificação SQLModel | [x] OK / [ ] Falha / [ ] N/A | <detalhes> |
| Posicionamento de Testes (Unit vs Integration) | [x] OK / [ ] Falha | <detalhes> |
| Validação Local (Linter / Testes) | [x] OK / [ ] Falha | <Baseado em pr-validation.json e execuções em tempo real> |
| Qualidade da Descrição e Governança | [x] OK / [ ] Falha | <detalha se o PR mapeia issues, nota de ciclo de vida para develop e possui estruturação temática no padrão do PR #267> |
| Status de Conflito (Mergeable) | [x] Sem Conflitos / [ ] Com Conflitos | <detalha se a branch do PR pode ser mergeada na branch de destino de forma limpa, baseado na chave `mergeable` do pr-context.json> |

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

## Rascunho para ARCHITECTURE.md / AGENTS.md (Se Aplicável)
> Se esta PR consolida uma nova decisão arquitetural durável, sugira o rascunho formatado para ser inserido na seção "ADRs — Architecture Decision Records" de `ARCHITECTURE.md` ou diretrizes do `AGENTS.md`:
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

- Nunca assumir que o código está correto sem verificar o arquivo real; use o `git` ou `gh` para coletar o status e o diff, e o repositório local para ler o código.  
- **Desconfie de PRs massivas**: Se uma PR altera muitos arquivos sob a justificativa de "lint" ou "formatação", você deve auditar pelo menos 5 arquivos aleatórios usando `git diff -w` para garantir que não há regressão de lógica ou arquitetura escondida.
- Se houver ambiguidade sobre camada, responsabilidade ou decisão, **sempre referenciar explicitamente** o que `ARCHITECTURE.md` ou `AGENTS.md` já consolida.
- **Blindagem de Ports**: Se o projeto já consolidou o uso de Ports (Interfaces), qualquer retorno ao uso de classes concretas em camadas superiores deve ser reportado como falha bloqueante de arquitetura.
- Evitar comentários de estilo triviais quando houver riscos arquiteturais ou de I/O mais relevantes.  
- Se a PR mexe em `squad-dashboard` ou CI/CD, lembre que labels e workflows alimentam o Squad Dashboard; trate isso com prioridade.
- Leia sempre os arquivos `.agents/scratch/pr-validation.json` e `.agents/scratch/pr-validation.log` se disponíveis, para enriquecer a seção de Validação Local no parecer.
- **Auditoria de Metadados do PR**: Analise a descrição (body) enviada no Pull Request. Se a descrição for considerada rasa (apenas uma lista plana ou sem referências a issues), aponte isso no review como uma pendência de documentação e sugira ativamente um rascunho de descrição robusto, copiando o modelo estruturado do PR #267.
- **Associação de Issues e Ciclo de Vida**:
  - Toda PR deve estar explicitamente vinculada a todas as issues resolvidas por ela. O revisor deve **obrigatoriamente listar os commits da branch** (ex: `git log develop..HEAD --oneline`) e cruzar com a lista de issues abertas do repositório (usando `gh issue list --limit 100`) para identificar e referenciar quaisquer issues adicionais resolvidas que não tenham sido incluídas na descrição original do PR.
  - Certifique-se de que a descrição do PR faça referência às issues de forma correta (ex: usando `Ref #XYZ` para manter o rastreamento sem disparar fechamento automático se a branch de destino for a `develop`).
  - **Transição Ativa de Status Labels**: Toda issue associada a um PR aberto/ativo deve ser atualizada para a label `status:review` (removendo `status:todo` ou `status:in_progress`) no momento da criação ou atualização do PR. Garanta que, ao fazer o merge na `develop`, as labels passem para `status:done` (permanecendo abertas), e sejam fechadas definitivamente apenas quando mescladas na branch `main`.

