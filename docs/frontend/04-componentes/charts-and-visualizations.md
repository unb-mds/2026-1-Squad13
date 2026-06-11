# Catálogo de Componentes - Gráficos e Visualizações

Este documento descreve os componentes visuais de dados e painéis analíticos baseados em gráficos no LexTrack.

## 1. Visualizações Recharts

A aplicação utiliza a biblioteca **Recharts** para renderizar gráficos interativos e responsivos que se adaptam aos dados retornados do backend:

### A. Gráfico de Evolução Temporal (`LineChart`)
* **Onde aparece:** No centro esquerdo da dashboard principal.
* **Objetivo:** Exibir a quantidade mensal de proposições legislativas que deram entrada ou saída (encerramento) no sistema de monitoramento.
* **Estrutura:**
  * **XAxis:** Eixo de meses (ex: `Jan/26`, `Fev/26`).
  * **YAxis:** Contador numérico de proposições.
  * **Séries:** Uma linha azul-petróleo (`--primary`) para **Entradas** e uma linha verde-limão (`--volt-400`) para **Saídas**.
  * **Tooltip:** Estilização customizada em conformidade com o tema de cores em [dashboard-page.tsx](../../../frontend/src/pages/dashboard-page.tsx#L447-L456).

### B. Gráfico de Tempo Médio por Comissão e Tipo (`BarChart`)
* **Onde aparece:** Widget de Gargalos e painéis analíticos.
* **Objetivo:** Exibir o tempo médio de tramitação acumulado.
* **Variações:**
  * *Vertical:* Usado na lista de comissões/órgãos para facilitar a leitura de rótulos de texto longos.
  * *Horizontal:* Usado na distribuição por tipo de proposição.

---

## 2. Widget de Cobertura de Dados (Gauges de Progresso)

### Visão Geral e Objetivo
Exibe 4 barras horizontais que indicam o nível de integridade, completude de metadados e confiabilidade do banco de dados analítico do LexTrack. 

### Onde Aparece
* Lateral direita do dashboard em [dashboard-page.tsx](../../../frontend/src/pages/dashboard-page.tsx#L486-L558).

### Estrutura
O componente não utiliza bibliotecas de gráficos complexas; ele é implementado por meio de estruturas HTML semânticas estilizadas com classes utilitárias do Tailwind CSS.

* **Barra de Progresso:** Um container com altura fixa (`h-2 bg-secondary`) que encapsula uma div animada interna (`h-full rounded-full transition-all`) com a propriedade `style={{ width: "[VALOR]%" }}` controlada por estado do React.
* **Coloração Dinâmica (Regras de UX):**
  * Se valor `>= 80%`: Classe `bg-emerald-500` (Verde - Nível Excelente).
  * Se valor `>= 50%` e `< 80%`: Classe `bg-amber-500` (Amarelo - Atenção).
  * Se valor `< 50%`: Classe `bg-red-500` (Vermelho - Crítico).

---

## 3. Diagramas de Trânsito entre Casas (`HouseTransitDiagram`)
* **Onde aparece:** Detalhes da proposição em [detalhe-proposicao-page.tsx](../../../frontend/src/pages/detalhe-proposicao-page.tsx#L296).
* **Objetivo:** Renderizar um fluxo gráfico simplificado que rastreia visualmente a remessa e o retorno de matérias legislativas entre a Câmara dos Deputados e o Senado Federal.

---

## 4. Problemas e Oportunidades Identificados
* **Tooltips Redundantes:** O componente `CustomTooltip` está declarado como função interna inline em `DashboardComponents.tsx` e recriado implicitamente em `dashboard-page.tsx` no componente `<Tooltip />` do Recharts.
  * *Recomendação:* Centralizar o estilo e a renderização de Tooltips em um componente compartilhado em `src/shared/components/`.
* **Layout Skeletons:** Gráficos do Recharts exibem apenas um loader simples ou bloco pulsante durante o estado de carregamento.
  * *Recomendação:* Implementar um mockup de gráfico de linhas em baixa opacidade (como SVG estático) para funcionar como um esqueleto de carregamento premium de visualização.

---

## 5. Arquivos Relacionados
* **Dashboard Page:** [dashboard-page.tsx](../../../frontend/src/pages/dashboard-page.tsx)
* **Gráficos Legados:** [DashboardComponents.tsx](../../../frontend/src/features/dashboard/DashboardComponents.tsx)
* **Diagrama de Trânsito:** [HouseTransitDiagram.tsx](../../../frontend/src/features/proposicoes/components/HouseTransitDiagram.tsx)
