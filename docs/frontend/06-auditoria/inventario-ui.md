# Auditoria de UI - Inventário Factual de Componentes

Este documento apresenta o mapeamento físico e funcional de arquivos, páginas e componentes no frontend do LexTrack, dividindo-os rigorosamente entre ativos (em produção e roteados) e inativos/legados (órfãos de uso).

---

## 1. Páginas (`frontend/src/pages/`)

| Arquivo Físico | Estado de Uso | Rota Associada | Descrição / Observações |
| :--- | :--- | :--- | :--- |
| [dashboard-page.tsx](../../../frontend/src/pages/dashboard-page.tsx) | **ATIVO** | `/dashboard` | Página principal de dados agregados, contendo buscas, gráficos, tabelas e mappers. |
| [detalhe-proposicao-page.tsx](../../../frontend/src/pages/detalhe-proposicao-page.tsx) | **ATIVO** | `/proposicoes/:id` | Visualização detalhada de uma proposição, integrando as timelines e cards de IA. |
| [consulta-proposicoes-page.tsx](../../../frontend/src/pages/consulta-proposicoes-page.tsx) | **INATIVO** | `/proposicoes` (Redirect) | Página órfã. O roteador (`AppRouter`) intercepta esta rota e redireciona para o `/dashboard`. |
| [relatorios-page.tsx](../../../frontend/src/pages/relatorios-page.tsx) | **INATIVO** | `/relatorios` (Redirect) | Página órfã. Rota redirecionada para `/dashboard` no roteador. |

---

## 2. Componentes Compartilhados (`frontend/src/shared/`)

### A. Componentes de UI Geral (`src/shared/ui/index.tsx`)
O arquivo [index.tsx](../../../frontend/src/shared/ui/index.tsx) atua como biblioteca atômica de UI. Todos os elementos a seguir estão **ATIVOS**, exceto pela duplicidade indicada:
* **Card, CardHeader, CardBody:** Utilizados em layouts de blocos secundários.
* **Badge:** Para rotular tipos e status de tramitações.
* **Button:** Botão interativo com loading state.
* **Input:** Campo de entrada com suporte a erros e ícones.
* **Select:** Menu suspenso estilizado.
* **Spinner:** Feedback de carregamento giratório.
* **EmptyState:** Utilizado na listagem de proposições em caso de erro ou busca vazia.
* **Pagination:** Controle de paginação de listas.
* **KpiCard (camelCase):** **ATIVO** nas sub-visualizações internas de gráficos. *Atenção: Duplicado em relação ao KPICard (PascalCase).*

### B. Componentes Semânticos (`src/shared/components/`)
* [KPICard.tsx](../../../frontend/src/shared/components/KPICard.tsx): **ATIVO** (PascalCase). Utilizado na linha de destaque do topo da `DashboardPage`.
* [InfoTooltip.tsx](../../../frontend/src/shared/components/InfoTooltip.tsx): **ATIVO**.
* [MetricCard.tsx](../../../frontend/src/shared/components/MetricCard.tsx): **ATIVO**.

---

## 3. Componentes de Módulos (`frontend/src/features/`)

### A. Feature: `dashboard`
* [DashboardComponents.tsx](../../../frontend/src/features/dashboard/DashboardComponents.tsx): **INATIVO**. Define componentes de estatísticas e gráficos isolados que foram replicados diretamente no corpo da `DashboardPage`.

### B. Feature: `filtros`
* [FilterChips.tsx](../../../frontend/src/features/filtros/FilterChips.tsx): **ATIVO**. Usado no Dashboard para remoção de tags de filtragem ativa.
* [PainelFiltros.tsx](../../../frontend/src/features/filtros/PainelFiltros.tsx): **INATIVO**. Utilizado exclusivamente pela página inativa `ConsultaProposicoesPage`.

### C. Feature: `proposicoes`
Todos os componentes na pasta [proposicoes/components/](../../../frontend/src/features/proposicoes/components/) estão **ATIVOS**, servindo às duas telas principais do sistema:
* **AIInsightsCard.tsx:** Exibe análise preditiva gerada por IA sobre as chances de aprovação.
* **BottleneckAnalytics.tsx:** Lista de órgãos e comissões com maiores taxas de retenção temporal.
* **DataReliability.tsx:** Indicador de qualidade de dados de trâmite legislativo.
* **EventTimeline.tsx:** Timeline granular de despachos e emendas.
* **HouseTransitDiagram.tsx & HouseTransitions.tsx:** Diagramas de fluxos de transição entre a Câmara e o Senado.
* **PhaseTimeline.tsx:** Timeline agregada por períodos de permanência.
* **PipelineStage.tsx:** Diagrama visual do funil do pipeline de aprovação de leis.
* **PropositionsTable.tsx:** Listagem principal de proposições com paginação no dashboard.

### D. Feature: `relatorios`
* [RelatorioComponents.tsx](../../../frontend/src/features/relatorios/RelatorioComponents.tsx): **INATIVO**. Vinculado à página inativa de relatórios.

### E. Feature: `tramitacoes`
Componentes legados provenientes de protótipos de desenvolvimento anteriores:
* [CardPrevisaoIA.tsx](../../../frontend/src/features/tramitacoes/CardPrevisaoIA.tsx): **INATIVO** (Substituído pela lógica em `AIInsightsCard.tsx`).
* [TimelineTramitacao.tsx](../../../frontend/src/features/tramitacoes/TimelineTramitacao.tsx): **INATIVO** (Substituído pelo `EventTimeline.tsx`).
