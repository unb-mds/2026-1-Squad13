# Catálogo de Componente - KPICard

Este documento cataloga o componente de exibição de métricas chaves (Key Performance Indicators) do LexTrack.

## 1. Visão Geral e Objetivo
O `KPICard` exibe um único indicador numérico ou textual acompanhado por um título, subtexto descritivo, ícone correspondente e indicador opcional de tendência percentual de evolução. É utilizado para dar visualização imediata da volumetria e andamento temporal do ecossistema legislativo.

---

## 2. Onde Aparece na Interface
* **Dashboard principal (`/dashboard`):** Na primeira linha de conteúdo da página, exibindo:
  * Total de proposições.
  * Proposições em tramitação ativa.
  * Proposições com atraso crítico (Modo Alarme).
  * Tempo mediano global de tramitação.

---

## 3. Estrutura e Propriedades (Props)
O componente ativo é implementado em [KPICard.tsx](../../../frontend/src/shared/components/KPICard.tsx) com a seguinte interface TypeScript:

```typescript
interface KPICardProps {
  title: string;          // Título descritivo da métrica
  value: string | number; // Valor em destaque (ex: "2.847" ou "54 dias")
  subtitle?: string;      // Subtexto de apoio inferior
  icon: LucideIcon;       // Ícone vetorial Lucide
  trend?: {
    value: string;        // Texto de tendência (ex: "+12% vs mês anterior")
    isPositive: boolean;  // Determina se a tendência é positiva (verde) ou negativa (vermelha)
  };
  isAlarm?: boolean;      // Ativa o visual de alerta crítico para atrasos
}
```

---

## 4. Estados e Variações Visuais

### A. Estado Normal / Padrão
* **Estilo:** Borda cinza neutra (`border-border`), fundo branco/card, ícone colorido na cor primária do tema.
* **Uso:** Total de proposições, tramitação ativa e tempo mediano.

### B. Estado de Alarme Crítico (`isAlarm = true`)
* **Estilo:** Adiciona uma borda esquerda vermelha de destaque (`border-l-4 border-l-red-600`), texto do valor principal em vermelho (`text-red-600`) e ícone vermelho sob um fundo claro avermelhado (`bg-red-100 text-red-600`).
* **Uso:** Card "Com Atraso Crítico".

### C. Tendências (Trend)
* **Positiva (`trend.isPositive = true`):** Renderiza o ícone `TrendingUp` e o texto na cor verde (`text-green-700`).
* **Negativa (`trend.isPositive = false`):** Renderiza o ícone `TrendingDown` e o texto na cor vermelha (`text-red-700`).

---

## 5. Problemas Identificados e Débito de Código
Durante a auditoria, identificamos uma **duplicação técnica de componente**:
1. **Ativo:** `KPICard` definido em [KPICard.tsx](../../../frontend/src/shared/components/KPICard.tsx) (utilizado no layout principal da `DashboardPage`).
2. **Duplicado/Legado:** `KpiCard` (grafado em camelCase/PascalCase semântico) definido na biblioteca de UI geral em [index.tsx](../../../frontend/src/shared/ui/index.tsx#L127-L150). Este último usa estilização fixa escura (`bg-ink-800`) e não suporta indicadores de tendência (`trend`) nem ícones personalizados em modo de alarme.

---

## 6. Oportunidades de Padronização
* **Unificação:** Mover as capacidades de tendência (`trend`) do `KPICard` ativo para o `KpiCard` de `shared/ui`, excluindo o arquivo `shared/components/KPICard.tsx` para eliminar a redundância de declaração.
* **Estilização Semântica:** Substituir as classes de estilização de cor fixa (ex: `bg-red-100` e `text-red-600`) por variáveis do tema Tailwind (ex: `bg-destructive/10 text-destructive`) para garantir suporte nativo e consistente a temas escuros.

---

## 7. Arquivos Relacionados
* **Implementação Ativa:** [KPICard.tsx](../../../frontend/src/shared/components/KPICard.tsx)
* **Implementação Redundante:** [shared/ui/index.tsx](../../../frontend/src/shared/ui/index.tsx#L127-L150)
* **Consumo do Componente:** [dashboard-page.tsx](../../../frontend/src/pages/dashboard-page.tsx#L353-L383)
