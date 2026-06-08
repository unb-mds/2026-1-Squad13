# Plano de Implementação: Filtros Ativos no Dashboard (Issue #91)

## Background & Motivation
Atualmente, o Dashboard exibe métricas globais e ignora a maioria dos filtros aplicados pelo usuário (como busca por texto, tipo de proposição ou período), exceto em alguns endpoints específicos. Para que o Dashboard seja uma ferramenta de análise real, todos os KPIs, gráficos e tabelas devem reagir dinamicamente aos filtros selecionados na interface.

## Scope & Impact
- **Módulos Afetados:**
  - **Backend:** `DashboardController`, `DashboardService`.
  - **Frontend:** `api.ts`, `useDashboard.ts`.
- **Impacto:** Alto valor para o usuário final (Release 2). Melhora a precisão analítica e permite drill-down por tipo, status e período.

## Proposed Solution

A implementação focará em garantir que os filtros fluam do Frontend até a camada de persistência em todos os endpoints de dashboard.

### Fase 1: Ajustes no Backend (Furo de Filtros)
A principal lacuna está no endpoint de tempo por fase, que hoje ignora filtros.
1.  **DashboardController:**
    - Alterar a rota `GET /dashboard/tempo-por-fase` para aceitar `filtros: DashboardFilterParams = Depends()`.
    - Converter para dict via `_montar_filtros(filtros)` e passar para o serviço.
2.  **DashboardService:**
    - Atualizar o método `obter_tempo_por_fase` para aceitar o parâmetro opcional `filtros: dict`.
    - Modificar a chamada interna `self.repository.filtrar()` para `self.repository.filtrar(**filtros)` (garantindo que o dict contenha apenas chaves aceitas pelo repositório).

### Fase 2: Ajustes no Frontend (Propagação)
1.  **Shared API (`api.ts`):**
    - Atualizar a função `obterTempoPorFase` para aceitar `filtros?: Partial<FiltrosProposicao>`.
    - Utilizar o helper `_filtrosParaParams(filtros)` para anexar a Query String na URL.
2.  **Dashboard Hook (`useDashboard.ts`):**
    - Na chamada `Promise.allSettled`, passar o estado atual de `filtros` para a função `obterTempoPorFase(filtros)`.

### Fase 3: Validação de Consistência
- Verificar se o método `_aplicar_filtros` no `SQLDashboardRepository` cobre todos os campos necessários:
  - `busca`, `tipo`, `status`, `orgao_origem`, `data_inicio`, `data_fim`.
- Garantir que a lógica de "Período" use a `data_apresentacao` como referência principal para proposições.

## Verification & Testing
1.  **Teste Manual (UI):**
    - Abrir o Dashboard.
    - Aplicar filtro de "Tipo: PEC".
    - Verificar se o KPI "Total de Proposições" e o gráfico "Pipeline Legislativo" refletem apenas dados de PECs.
    - Aplicar filtro de busca por termo específico (ex: "Tributária") e verificar a redução proporcional dos números.
2.  **Teste Automatizado (Pytest):**
    - Adicionar um caso de teste em `test_dashboard_service.py` validando que `obter_tempo_por_fase` retorna resultados diferentes quando filtros são aplicados.

## Alternatives Considered
- **Filtragem no Frontend:** Descartada por não ser escalável (o Dashboard deve processar milhares de registros no banco via agregadores SQL).
- **Cache por Filtro:** Já implementado no `DashboardService`, mas será necessário validar se a chave de cache (`_gerar_cache_key`) está incluindo todos os parâmetros de filtro novos. (Visto que o método já existe, deve funcionar).
