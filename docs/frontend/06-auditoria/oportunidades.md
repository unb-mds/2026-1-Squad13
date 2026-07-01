# Auditoria de UI - Oportunidades de Refatoração e Melhorias de Design

Este documento apresenta recomendações práticas e oportunidades de melhoria na arquitetura do frontend do LexTrack, visando aumentar a performance, manutenibilidade do código e estabilidade visual.

---

## 1. Eliminação de Código Morto (Dead Code Cleanup)
* **Problema:** Existência de múltiplos arquivos inativos (`relatorios-page.tsx`, `consulta-proposicoes-page.tsx`, `DashboardComponents.tsx`, `TimelineTramitacao.tsx`, `CardPrevisaoIA.tsx`).
* **Impacto:** Aumento desnecessário do tamanho do repositório e do bundle de produção compilado.
* **Recomendação:** Excluir fisicamente esses arquivos se as suas funcionalidades já tiverem sido consolidadas nas páginas de Dashboard ou Detalhes da Proposição, reduzindo a carga cognitiva e simplificando a árvore de dependências.

---

## 2. Unificação e Padronização do Componente de KPIs
* **Problema:** Presença de duas variações funcionais de card de métricas com estilos visuais e props inconsistentes (`KPICard` e `KpiCard`).
* **Impacto:** Desalinhamento visual nos fundos dos cards na visualização geral.
* **Recomendação:** 
  1. Manter a exportação centralizada em [index.tsx](../../../frontend/src/shared/ui/index.tsx) sob o nome PascalCase unificado `KPICard`.
  2. Adicionar as props opcionais `trend` e `isAlarm` na assinatura padrão do componente unificado.
  3. Excluir o arquivo [KPICard.tsx](../../../frontend/src/shared/components/KPICard.tsx) legado.

---

## 3. Semantização Completa do Tailwind (Suporte Seguro a Temas)
* **Problema:** Uso excessivo de classes de cores fixas do Tailwind (ex: `bg-ink-800` ou `bg-rose-500/15`) na biblioteca de UI básica, limitando o uso correto de temas do sistema.
* **Impacto:** Dificuldade para alternar de forma limpa entre Light Theme e Dark Theme.
* **Recomendação:** Refatorar as propriedades de cores dos componentes em [index.tsx](../../../frontend/src/shared/ui/index.tsx) para utilizarem variáveis de tema semânticas (como `bg-card`, `text-card-foreground`, `border-border`, `bg-destructive/15`), em vez de valores codificados de forma estática.

---

## 4. Desacoplamento de Lógicas de Negócio das Visualizações (Views)
* **Problema:** A [DashboardPage](../../../frontend/src/pages/dashboard-page.tsx) contém mais de 650 linhas de código, acumulando lógicas de paginação, formatação de chips de filtros avançados, triggers de debounce, manipulações de API e exportação de relatórios em formato JSON.
* **Impacto:** Torna o arquivo da página difícil de ler e testar de forma isolada (testes unitários).
* **Recomendação:**
  * Mover a lógica de paginação e filtragem da listagem de proposições para um hook de feature customizado (ex: `useDashboardPropositions`).
  * Extrair as funções utilitárias de exportação de dados para a camada de helpers/serviços compartilhados da aplicação (`src/shared/lib/utils/`).
