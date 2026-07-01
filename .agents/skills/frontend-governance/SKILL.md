---
name: frontend-governance
description: Use para tarefas de frontend, UI, layout, componentes, design tokens, documentação de frontend, ADRs ou decisões visuais no projeto LexTrack.
---

# Frontend Governance

Você é responsável por garantir a integridade, consistência e documentação do frontend do LexTrack. Sua missão é impedir mudanças silenciosas que quebrem o baseline visual ou o sistema de decisões estabelecido.

## Quando Usar
- Tarefas que envolvam React, Tailwind, CSS ou TypeScript no subprojeto `/frontend`.
- Criação, modificação ou remoção de componentes de UI.
- Alteração de Design Tokens (cores, fontes, espaçamentos).
- Discussões sobre layout, UX ou navegação.
- Necessidade de criar ou atualizar documentação de frontend ou ADRs.

## Quando NÃO Usar
- Mudanças exclusivas de backend (API, Banco de Dados, Workers) sem impacto na interface.
- Scripts de infraestrutura ou CI/CD que não afetem o build do frontend.

## Fontes Obrigatórias (Ler antes de agir)
1. `.agents/skills/frontend-governance/references/docs-index.md` (Para localizar guias específicos).
2. `docs/frontend/02-design-principles.md` e `03-design-tokens.md`.
3. ADRs de frontend em `docs/adr/`.

## Fluxo de Operação

### 1. Pesquisa e Classificação (Pré-Check)
Antes de propor ou implementar:
- Classifique a mudança: **Estrutural**, **Componente**, **Visual**, **Decisão** ou **Documentação**.
- Localize o baseline em `docs/frontend/`.
- Verifique se a mudança viola algum princípio documentado ou ADR.

### 2. Estratégia e Implementação
- Utilize **Design Tokens** do `tailwind.config.js`. NUNCA use valores "hardcoded".
- Siga a **Feature-Based Architecture**.
- Se a mudança for uma nova decisão de design, prepare a justificativa técnica.

### 3. Validação e Documentação (Pós-Check)
Após a implementação:
- Aplique o `references/review-checklist.md`.
- **Validação Local de Compilação/Linter:** Execute o build e linter do frontend localmente (`npm run lint` ou `npm run build` na pasta `/frontend`) usando as ferramentas do Antigravity CLI para certificar-se de que a alteração não introduz erros de compilação ou de tipagem (TypeScript).
- Verifique conforme `references/update-rules.md` se é necessário:
   - Atualizar arquivos em `docs/frontend/`.
   - Criar uma ADR (`templates/adr-template.md`).
   - Registrar no log de mudanças (`templates/change-log-template.md`).
   - Abrir issues de follow-up se houver dívida técnica introduzida intencionalmente.

## Regras de Ouro
- **Código > Figma:** O código é a fonte da verdade operacional. Se houver divergência, consulte a documentação ou peça esclarecimento.
- **Rastreabilidade:** Nenhuma decisão visual relevante deve passar sem registro (ADR ou UI Decision Log).
- **Consistência:** Prefira composição de componentes existentes a criar novos quase idênticos.
