# AGENTS.md - Diretrizes do Squad Dashboard

Este guia orienta agentes de IA atuando na pasta `squad-dashboard/` do LexTrack.

## 1. Objetivo do Painel
O **Squad Dashboard** é uma aplicação estática e independente para coletar e exibir dados do repositório (commits, PRs, issues) e tempo de ciclo de desenvolvimento.

## 2. Comandos e Sincronização
* **Sincronizar Metadados do GitHub:** Rodar `./squad-dashboard/scripts/sync-github-metadata.sh`
* **Executar no diretório `squad-dashboard/`:**
  * Instalar dependências: `npm install`
  * Servidor de desenvolvimento: `npm run dev`
  * Executar testes: `npm run test`
  * Gerar build estático: `npm run build`

## 3. Definition of Done (DoD Local)
1. Garantir que a compilação local via `npm run build` passa sem erros após qualquer modificação.
2. Certificar que novos gráficos ou tabelas consomem adequadamente o payload do GitHub gerado na sincronização.
