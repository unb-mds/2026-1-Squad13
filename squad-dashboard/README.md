# Squad Dashboard — Squad 13

Painel de produtividade e evolução do Squad 13 durante o desenvolvimento do **Monitoramento de Tramitação de Leis**.

Projeto **completamente separado** do sistema principal — sem backend, sem integração, dados locais em `src/mocks/`.

---

## Dados em tempo real — GitHub

O dashboard consome dados reais do repositório `unb-mds/2026-1-Squad13` quando disponíveis.
Caso contrário, usa os mocks de `src/mocks/` como fallback automático — sem quebrar nada.

### Como funciona o pipeline

```
GitHub Actions (cron a cada 6h ou manual)
  └→ scripts/generate-github-data.mjs
       └→ GitHub REST API (commits, PRs, issues, workflows, contributors)
            └→ public/data/github-stats.json  ← commitado no repositório
                 └→ deploy-squad-dashboard.yml reconstrói e publica
                      └→ GitHub Pages serve o JSON como arquivo estático
                           └→ useGithubData() faz fetch no runtime
                                └→ fallback para mocks se ausente ou inválido
```

### Onde ficam os JSON

```
squad-dashboard/public/data/
└── github-stats.json   ← gerado automaticamente; não edite manualmente
```

Em produção (GitHub Pages), o arquivo é servido em:
`https://unb-mds.github.io/2026-1-Squad13/data/github-stats.json`

### Como atualizar os dados manualmente

**Via GitHub Actions (recomendado):**
1. Acesse **Actions → Update Squad Dashboard Data** no repositório.
2. Clique em **Run workflow**.
3. O JSON é gerado, commitado em `main` e o deploy atualiza automaticamente.

**Localmente (para desenvolvimento):**
```bash
GITHUB_TOKEN=ghp_seu_token_aqui node squad-dashboard/scripts/generate-github-data.mjs
```
O arquivo gerado em `public/data/github-stats.json` será servido por `npm run dev`.

### Como funciona o fallback

O hook `useGithubData()` (`src/shared/api/github-data-service.ts`) tenta fazer fetch do JSON.
Se o fetch falhar (404 em dev sem arquivo gerado, rede indisponível, JSON inválido), retorna `null`
e cada widget/página usa os dados de `src/mocks/` transparentemente.

### Campos disponíveis no JSON

| Campo | Descrição |
|-------|-----------|
| `generatedAt` | ISO 8601 da geração — `null` no placeholder |
| `commitsByDay` | Commits dos últimos 7 dias (para o gráfico de barras) |
| `commitsByAuthor` | Commits agrupados por autor |
| `weeklyCommits` | Commits das últimas 8 semanas |
| `pullRequests` | `open`, `merged`, `closed` |
| `issues` | `open`, `closed` (excluindo PRs) |
| `recentWorkflows` | Últimas 10 execuções de CI/CD |
| `contributors` | Lista de contribuidores com avatar |

### Como testar no GitHub Pages

Após o deploy, acesse:
- Dashboard: `https://unb-mds.github.io/2026-1-Squad13/`
- JSON gerado: `https://unb-mds.github.io/2026-1-Squad13/data/github-stats.json`

---

## Deploy — GitHub Pages

URL pública: **https://unb-mds.github.io/2026-1-Squad13/**

O deploy é automático via GitHub Actions (`.github/workflows/deploy-squad-dashboard.yml`).
Dispara em push para `main` ou `feature/squad-productivity-dashboard` quando arquivos de `squad-dashboard/` são alterados.

### Ativar GitHub Pages (primeira vez)

1. Acesse **Settings → Pages** no repositório.
2. Em **Source**, selecione **GitHub Actions**.
3. Salve. O próximo push ativa o deploy automaticamente.

---

## Como rodar localmente

```bash
cd squad-dashboard
npm install
npm run dev
# → http://localhost:5173
```

---

## Páginas

| Rota | Página | Conteúdo |
|------|--------|----------|
| `/` | Dashboard | KPIs do projeto, progresso por feature, gráficos semanais e burndown do sprint atual |
| `/board` | Board | Kanban com tasks reais do sprint — Backlog, Todo, In Progress, Review, Done |
| `/features` | Features | Progresso de cada funcionalidade com blockers, responsável e prazo |
| `/team` | Time | Cards dos integrantes com métricas individuais de produtividade |
| `/roadmap` | Roadmap | Timeline de sprints e milestones do projeto |

---

## Como atualizar os dados

### Trocar nomes dos integrantes

Edite `src/mocks/team.ts` — cada integrante tem um comentário `// <- edite o nome aqui`:

```ts
{
  id: 'm1',
  name: 'Kaiky',       // <- troque pelo nome real
  avatarInitials: 'KA', // <- iniciais para o avatar
  ...
}
```

Os IDs (`m1`…`m5`) são referenciados em `tasks.ts` e `features.ts`. **Não altere os IDs** — só os dados de texto e métricas.

### Atualizar métricas globais

Edite `src/mocks/metrics.ts` — o objeto `mockKpis`:

```ts
export const mockKpis = {
  tasksDone: 12,         // tasks concluídas (soma real)
  prsMerged: 5,          // PRs mergeados no repo
  coveragePercent: 28,   // cobertura atual de testes (%)
  overallProgress: 32,   // progresso geral estimado (%)
  ...
}
```

### Atualizar progresso das features

Edite `src/mocks/features.ts` — campos `progress`, `tasksDone` e `blockers`:

```ts
{
  id: 'f1',
  name: 'Consulta de Proposições',
  progress: 64,       // percentual 0-100
  tasksDone: 9,       // tasks concluídas
  blockers: [],       // lista de textos de bloqueio
  ...
}
```

### Adicionar tasks ao board

Edite `src/mocks/tasks.ts`. Cada task segue o padrão:

```ts
{
  id: 't26',                         // id único
  title: 'Nome da task',
  status: 'todo',                    // backlog | todo | in_progress | review | done
  priority: 'high',                  // critical | high | medium | low
  labels: ['feature'],               // feature | bug | chore | docs | test
  assigneeId: 'm2',                  // id de src/mocks/team.ts
  featureId: 'f3',                   // id de src/mocks/features.ts
  dueDate: '2026-06-15',
  progress: 0,                       // 0-100 (relevante em in_progress)
  createdAt: '2026-05-11',
}
```

### Atualizar sprint ativo

Edite `src/mocks/sprints.ts` — mude `status: 'active'` para o sprint correto e ajuste `tasksDone`.
Atualize também o texto em `src/widgets/sidebar.tsx` (linha do indicador "Sprint N · ativo").

---

## Features do projeto

| ID | Feature | Status atual |
|----|---------|-------------|
| f1 | Consulta de Proposições | Em Progresso (64%) |
| f2 | Detalhamento da Proposição | Em Progresso (15%) |
| f3 | Dashboard Analítico | Planejada |
| f4 | Inteligência Preditiva | Planejada |
| f5 | Autenticação | Planejada |
| f6 | Infraestrutura & Arquitetura | Em Progresso (90%) |
| f7 | Qualidade & CI/CD | Em Progresso (55%) |

---

## Stack

- **React 18** + **TypeScript** — framework e tipagem
- **Vite** — build tool
- **Tailwind CSS** — estilização
- **Recharts** — gráficos (area, line, bar, radar)
- **Lucide React** — ícones
- **React Router v6** — roteamento

---

## Arquitetura

```
src/
├── app/          # App.tsx + roteamento
├── pages/        # Uma página por rota (dashboard, board, features, team, roadmap)
├── widgets/      # Compostos cross-cutting (KpiCard, charts, Sidebar)
├── features/     # Componentes com domínio visual (board, feature-tracker, team)
├── entities/     # Tipos TypeScript puros (Task, Member, Feature, Sprint)
├── shared/       # Primitivos reutilizáveis (Badge, Avatar, ProgressBar, Skeleton)
└── mocks/        # Fonte única de dados — edite aqui para atualizar o painel
    ├── team.ts       ← integrantes e métricas individuais
    ├── tasks.ts      ← tasks do kanban
    ├── features.ts   ← features e progresso
    ├── sprints.ts    ← roadmap e milestones
    └── metrics.ts    ← KPIs globais e dados dos gráficos
```

---

## Git

Branch: `feature/squad-productivity-dashboard`
Não fazer commit automático — revisar antes de abrir PR para `main`.
