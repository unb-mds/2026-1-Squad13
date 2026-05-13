# Automação do Squad Dashboard

Este documento detalha como o dashboard consome dados dinâmicos do GitHub e como manter essa integração.

## 🔄 Fluxo de Dados (Pipeline)

1.  **Extração**: O script `scripts/generate-github-data.mjs` é executado via GitHub Actions a cada 6 horas ou em cada push na `main`.
2.  **API do GitHub**: O script consome os endpoints de Commits, Issues, Pull Requests, Milestones e Actions.
3.  **Payload**: É gerado um arquivo estático em `public/data/github-stats.json`.
4.  **Consumo**: O frontend React consome este JSON através do hook `useGithubData`.

## 🏷️ Mapeamento de Features (Labels)

O progresso das funcionalidades é calculado automaticamente baseado em **Labels**. Para que uma issue contribua para o progresso de uma feature, ela deve possuir a label correspondente:

| ID | Feature | Label GitHub |
|---|---|---|
| f1 | Consulta de Proposições | `feat:f1` |
| f2 | Detalhamento da Proposição | `feat:f2` |
| f3 | Dashboard Analítico | `feat:f3` |
| f4 | Inteligência Preditiva | `feat:f4` |
| f5 | Autenticação | `feat:f5` |
| f6 | Infraestrutura & Arquitetura | `feat:f6` |
| f7 | Qualidade & CI/CD | `feat:f7` |

**Cálculo**: `% Conclusão = (Issues Fechadas / Total de Issues) * 100`.

## 📉 Gráfico de Burndown

O burndown é gerado analisando o histórico de criação e fechamento de issues nos últimos 20 dias. Ele compara o "Restante" (issues abertas) com a "Linha Ideal" calculada para o período.

## 🛡️ Qualidade e Cobertura

O dashboard tenta ler o arquivo `coverage/coverage-summary.json`. Se o Vitest for executado com a flag `--coverage` antes da geração dos dados, o percentual de cobertura real aparecerá no KPI do Dashboard.
