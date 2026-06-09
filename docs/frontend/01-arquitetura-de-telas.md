# 01 - Arquitetura de Telas e Navegação

Este documento mapeia o ecossistema de telas do LexTrack, detalhando a configuração de rotas e o comportamento do fluxo de navegação do usuário.

## Configuração do Roteamento (`AppRouter`)
O roteamento no frontend é definido no componente central `AppRouter` em [index.tsx](../../frontend/src/app/router/index.tsx), utilizando a biblioteca **React Router** (`react-router-dom`).

```typescript
export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="proposicoes" element={<Navigate to="/dashboard" replace />} />
          <Route path="proposicoes/:id" element={<DetalheProposicaoPage />} />
          <Route path="relatorios" element={<Navigate to="/dashboard" replace />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
```

---

## Mapeamento de Rotas e Telas

O sistema é estruturado em duas telas funcionais ativas e três redirecionamentos de fallback:

### 1. Rota Raiz (`/`)
* **Layout:** Utiliza o [AppLayout](../../frontend/src/app/layouts/AppLayout.tsx) como casca global de renderização (veja [Layout Shell](./01b-layout-shell.md) para mais detalhes).
* **Ação:** Redireciona imediatamente (`Navigate replace`) para a rota `/dashboard`.

### 2. Tela Principal do Dashboard (`/dashboard`)
* **Componente:** `DashboardPage` em [dashboard-page.tsx](../../frontend/src/pages/dashboard-page.tsx).
* **Função:** É o centro operacional do sistema. Consolida:
  * Cards de Indicadores (KPIs) de trâmite geral.
  * O gráfico de evolução temporal.
  * O widget de **Cobertura de Dados**.
  * A tabela de proposições legislativas ativas (`PropositionsTable`) com buscas e ordenação.
  * O painel lateral/gaveta de Filtros Avançados.
  * O gráfico de gargalos organizados por comissão, fase e tema.

### 3. Tela de Detalhes da Proposição (`/proposicoes/:id`)
* **Componente:** `DetalheProposicaoPage` em [detalhe-proposicao-page.tsx](../../frontend/src/pages/detalhe-proposicao-page.tsx).
* **Função:** View de drill-down profundo para uma única proposição parlamentar. Apresenta:
  * Metadados detalhados (autor, ementa, link oficial, etc.).
  * Pipeline gráfico de fases da proposição (`PhaseTimeline`).
  * Trilha detalhada de eventos legislativos normalizados (`EventTimeline`).
  * Diagrama gráfico de transições entre a Câmara e o Senado (`HouseTransitDiagram`).
  * Card analítico preditivo gerado por Inteligência Artificial (`AIInsightsCard`).
  * Widget de confiabilidade e completude dos dados (`DataReliability`).

---

## Rotas Inativas e Legados de Navegação
Durante a auditoria arquitetural, observou-se que duas páginas existentes na pasta de páginas estão **inativas** no roteador principal:

1. **Consulta de Proposições (`/proposicoes`):**
   * *Status:* Redireciona para `/dashboard`.
   * *Arquivo Órfão:* [consulta-proposicoes-page.tsx](../../frontend/src/pages/consulta-proposicoes-page.tsx).
   * *Justificativa:* A tabela e filtros principais foram consolidados diretamente na `DashboardPage` para reduzir a fricção e centralizar a investigação do usuário em uma única área de triagem.
2. **Visualização de Relatórios (`/relatorios`):**
   * *Status:* Redireciona para `/dashboard`.
   * *Arquivo Órfão:* [relatorios-page.tsx](../../frontend/src/pages/relatorios-page.tsx).
   * *Justificativa:* Os indicadores analíticos de relatórios foram acoplados diretamente ao widget de **Gargalos** na `DashboardPage`.

*Nota: A preservação desses arquivos órfãos sem roteamento é mantida como histórico/especificação técnica (baseline), devendo ser limpa ou refatorada de acordo com as regras estabelecidas na [Governança de UI](./07-governanca/regras-de-evolucao-ui.md).*

---

## Próximos Passos recomendados para Leitura
* Para entender o dimensionamento físico do container principal e a responsividade, veja o [Layout Shell](./01b-layout-shell.md).
* Para detalhes de comportamento e transições na visualização de dados, consulte o [Catálogo de Componentes](./04-componentes/kpi-card.md).
