# ADR-008: GitHub Actions como pipeline de dados para o Squad Dashboard

**Data:** 2026-05-11  
**Status:** Aceita  
**Decisores:** Arquiteto, Dev  

---

## Contexto

O Squad Dashboard (ADR-007) foi criado inicialmente com dados editoriais em `src/mocks/`. Com o tempo, manter métricas como PRs mergeados, commits por dia, contributors e execuções de CI manualmente tornou-se trabalhoso e propenso a desatualização.

O dashboard precisava consumir dados reais do repositório `unb-mds/2026-1-Squad13` sem:

- Expor o `GITHUB_TOKEN` no código do frontend (risco de segurança)
- Depender de uma conta ou plano pago na GitHub API (rate limit de 60 req/h sem autenticação)
- Criar ou reutilizar o backend FastAPI para uma responsabilidade alheia ao domínio legislativo
- Adicionar infraestrutura nova (servidor, banco, workers) para uma ferramenta acessória

O dashboard é uma SPA estática hospedada no GitHub Pages — sem servidor de aplicação, sem runtime server-side.

---

## Decisão

Vamos usar **GitHub Actions** como pipeline de geração de dados, produzindo arquivos JSON estáticos consumidos pelo dashboard em tempo de execução no browser.

Fluxo completo:

```
GitHub Actions (cron a cada 6h ou acionamento manual)
  └→ scripts/generate-github-data.mjs
       └→ GitHub REST API v3 (~5 requisições autenticadas)
            └→ squad-dashboard/public/data/github-stats.json
                 └→ commit automático em main
                      └→ dispara deploy-squad-dashboard.yml
                           └→ vite build copia public/ → dist/
                                └→ GitHub Pages serve /data/github-stats.json
                                     └→ useGithubData() faz fetch no browser
                                          └→ fallback para mocks se ausente ou inválido
```

**Dois workflows complementares:**

1. `update-squad-dashboard-data.yml` — responsável exclusivo pela geração de dados:
   - Dispara via `schedule` (cron `0 */6 * * *`) e `workflow_dispatch`
   - **Não dispara em push** — evita loops de commit
   - Usa `GITHUB_TOKEN` automático do Actions (gerado por job, expira ao fim, nunca exposto)
   - Commita o JSON em `main` apenas se houver mudança (`git diff --staged --quiet ||`)
   - O commit em `main` dispara o workflow de deploy

2. `deploy-squad-dashboard.yml` — responsável pelo build e publicação:
   - Executa `scripts/generate-github-data.mjs` como step antes do build (`continue-on-error: true`)
   - Garante dados frescos em cada deploy independente do cron ter rodado
   - Se a geração falhar, o deploy continua com o JSON anterior (ou placeholder)

**Script de geração** (`scripts/generate-github-data.mjs`):
- Node 18+ com `fetch` nativo — sem dependências extras
- 5 chamadas à GitHub REST API v3:
  - `GET /repos/{owner}/{repo}/commits` — commits por dia e por autor
  - `GET /repos/{owner}/{repo}/pulls?state=all` — PRs abertos, mergeados e fechados
  - `GET /repos/{owner}/{repo}/issues?state=all` — issues (excluindo PRs)
  - `GET /repos/{owner}/{repo}/actions/runs` — execuções recentes de CI/CD
  - `GET /repos/{owner}/{repo}/contributors` — contributors com contagem de commits
- Escreve em `public/data/github-stats.json` usando `__dirname` para resolução de caminho independente de diretório de execução

**Estratégia de fallback** no hook `useGithubData()` (`src/shared/api/github-data-service.ts`):
- `fetch()` para `{BASE_URL}data/github-stats.json`
- Se `generatedAt === null`: placeholder detectado — retorna `null`
- Se fetch falhar (404 em dev local, rede indisponível): retorna `null`
- Quando `null`, cada widget/página usa os dados de `src/mocks/` transparentemente
- Nenhum estado de erro exibido ao usuário — degradação silenciosa

**Placeholder seguro para versionamento** (`public/data/github-stats.json`):

```json
{
  "generatedAt": null,
  "_note": "Placeholder — dados reais gerados pelo workflow update-squad-dashboard-data.yml"
}
```

Commitado no repositório para que o arquivo exista em dev local e no GitHub Pages antes do primeiro cron. O campo `generatedAt: null` sinaliza ao hook que o arquivo é inerte.

---

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| GitHub Actions → JSON estático (escolhida) | Token nunca no frontend; zero infraestrutura extra; fallback automático | Dados com até 6h de defasagem; JSON público no repositório |
| Frontend chamando GitHub API diretamente | Dados sempre frescos | `GITHUB_TOKEN` exposto no código ou 60 req/h sem autenticação — inviável em produção |
| Backend FastAPI como proxy da GitHub API | Token protegido no servidor | Responsabilidade alheia ao domínio do produto; aumenta carga e acoplamento do backend principal |
| Servidor dedicado (Express, Hono) | Separação de responsabilidades | Infraestrutura e custo adicionais para uma ferramenta acessória |
| Atualização manual dos mocks | Zero automação | Dados desatualizados constantemente; trabalho operacional recorrente |
| GitHub GraphQL API | Menos requisições; mais dados por chamada | Adiciona complexidade de query language sem ganho significativo para os dados coletados |

---

## Consequências

**Positivas:**
- `GITHUB_TOKEN` nunca presente no código do frontend — risco de vazamento eliminado
- Zero infraestrutura adicional: pipeline inteiro roda dentro do GitHub, sem custo extra
- Dados automáticos a cada 6 horas sem intervenção manual
- Fallback transparente: dashboard funciona mesmo sem dados reais, sem erros visíveis ao usuário
- Script sem dependências externas (Node 18+ nativo) — sem `npm install` adicional no workflow de dados
- Acionamento manual (`workflow_dispatch`) permite atualização imediata sob demanda

**Negativas / trade-offs:**
- Dados com até 6h de defasagem em relação ao repositório real
- JSON gerado é público no repositório (`public/data/`) — aceitável pois são dados já públicos do repositório
- O commit automático do cron cria entradas no histórico git — mitigação parcial com mensagem padronizada `[auto]`
- `continue-on-error: true` no step de geração do deploy significa que falhas na API passam silenciosamente

**Riscos:**
- GitHub REST API fora do ar durante o cron impede atualização dos dados — mitigação: fallback para o JSON anterior ou para mocks; o painel continua funcional
- Mudança no nome ou visibilidade do repositório pode invalidar as rotas da API — mitigação: a URL do repositório está centralizada na variável `REPO` no script, alteração em um único ponto
- Aumento futuro das chamadas pode aproximar o limite de 5.000 req/h do `GITHUB_TOKEN` — mitigação: o script faz apenas ~5 requisições por execução; margem de mais de 800x antes do limite
- Dados sensíveis presentes no repositório poderiam vazar via JSON — mitigação: o script coleta apenas metadados públicos (commits, PRs, issues, contributors) já visíveis na interface do GitHub
