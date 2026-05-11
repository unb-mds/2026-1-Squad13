# ADR-007: Squad Dashboard como projeto standalone deployado no GitHub Pages

**Data:** 2026-05-11  
**Status:** Aceita  
**Decisores:** Arquiteto, Dev  

---

## Contexto

O Squad 13 precisava de um painel de acompanhamento de produtividade — tarefas, progresso por feature, métricas de sprint, roadmap e informações do time — para uso interno durante o desenvolvimento do Monitoramento de Tramitação de Leis.

Fatores relevantes:

- O painel não é parte do produto entregável — é uma ferramenta interna do time
- O backend principal (FastAPI + PostgreSQL) serve o domínio legislativo e não deve ser sobrecarregado com dados de produtividade do squad
- O time não possui infraestrutura de hosting paga disponível para uma ferramenta acessória
- Os dados iniciais do painel são editoriais (manutenção manual via mocks) — não exigem persistência em banco
- A stack do painel deve ser familiar para o time (React + TypeScript + Vite + Tailwind), evitando curva de aprendizado adicional
- O painel precisa ser acessível a todos os integrantes via URL pública, sem configuração local

---

## Decisão

Vamos criar o `squad-dashboard/` como um **projeto Vite standalone**, completamente separado de `frontend/` e `backend/`, e deployá-lo no **GitHub Pages** via GitHub Actions.

Isolamento:
- Diretório próprio com `package.json`, `tsconfig.json`, `vite.config.ts` e `.gitignore` independentes
- Nenhuma importação ou dependência compartilhada com `frontend/` ou `backend/`
- Dados centralizados em `src/mocks/` — fonte única editorial, sem integração com APIs do sistema

Arquitetura interna: **Feature-Based Architecture simplificada**, alinhada ao padrão já adotado em `frontend/` (ADR implícito):

```
src/
├── app/        # roteamento
├── pages/      # uma por rota
├── widgets/    # compostos cross-cutting (gráficos, sidebar)
├── features/   # componentes com domínio visual (board, team, features-tracker)
├── entities/   # tipos TypeScript puros
├── shared/     # primitivos reutilizáveis (Badge, Avatar, ProgressBar)
└── mocks/      # fonte única de dados editoriais
```

**HashRouter em vez de BrowserRouter:**

GitHub Pages serve arquivos estáticos. Quando o usuário acessa `/board` diretamente ou recarrega a página, o servidor procura `board/index.html` — que não existe — e retorna 404. Com `HashRouter`, a URL vira `/#/board`: o servidor sempre resolve `index.html` (parte antes do `#`), e o React Router lê o fragmento.

```tsx
// src/main.tsx
import { HashRouter } from 'react-router-dom'
// URLs resultantes: /#/board, /#/team, /#/roadmap
```

**Base path do Vite:**

GitHub Pages serve o repositório em `/2026-1-Squad13/`. Sem configuração, os assets do build apontam para `/assets/` — endereço inexistente no hosting. A propriedade `base` corrige isso:

```ts
// vite.config.ts
export default defineConfig({
  base: '/2026-1-Squad13/',
  // assets gerados: /2026-1-Squad13/assets/index-*.js
})
```

**Workflow de deploy** (`.github/workflows/deploy-squad-dashboard.yml`):
- Dispara em push para `main` ou `feature/squad-productivity-dashboard` com `paths: squad-dashboard/**`
- Usa `actions/configure-pages` + `upload-pages-artifact` + `deploy-pages` (stack oficial GitHub)
- `concurrency: group: pages` evita deploys simultâneos conflitantes

---

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| GitHub Pages (escolhida) | Zero custo; integrado ao repositório; deploy automático via Actions | URLs com `#`; base path acoplado ao nome do repositório |
| Vercel / Netlify | SPA routing nativo; domínio customizado | Conta externa; dependência de serviço terceiro; mais configuração |
| GitHub Pages + 404.html redirect | Mantém BrowserRouter; URLs sem `#` | Frágil; hack não oficial; pode quebrar em atualizações do Pages |
| Integrar ao `frontend/` principal | Menos projetos para manter | Viola separação de domínios; polui o frontend do produto com ferramenta interna |
| Sem deploy (apenas local) | Zero configuração | Não acessível ao time sem setup local; não serve para demonstrações |

---

## Consequências

**Positivas:**
- Painel acessível publicamente via URL única sem qualquer setup local
- Deploy automático a cada push — o painel reflete sempre o estado atual da branch
- Zero custo de infraestrutura — GitHub Pages é gratuito para repositórios públicos
- Isolamento completo: nenhuma alteração no painel afeta `frontend/`, `backend/` ou os CIs existentes
- Stack idêntica ao `frontend/` principal — sem curva de aprendizado adicional para o time

**Negativas / trade-offs:**
- URLs com fragmento `#` (ex: `/#/board`) em vez de rotas limpas — impacto cosmético aceitável para ferramenta interna
- O valor de `base` no `vite.config.ts` está acoplado ao nome do repositório — mudar o nome do repositório exigiria atualizar esse campo
- Dois projetos Node separados (`frontend/` e `squad-dashboard/`) com dependências que precisam ser mantidas individualmente
- Dados editoriais (tasks, features, sprints) precisam de atualização manual em `src/mocks/`

**Riscos:**
- GitHub Pages fora do ar bloqueia acesso ao painel — mitigação: o painel é uma ferramenta acessória, não crítica para o produto
- Confusão entre `squad-dashboard/` e `frontend/` por membros novos — mitigação: README e comentários no código deixam claro que são projetos independentes
- Dependências do `squad-dashboard/` desatualizadas ao longo do tempo — mitigação: `npm audit` e renovação periódica, independente do ciclo do produto
