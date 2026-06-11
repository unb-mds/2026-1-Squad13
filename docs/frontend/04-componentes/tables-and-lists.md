# Catálogo de Componentes - Tabelas e Paginação

Este documento detalha o componente de visualização tabular de proposições e o controle de paginação do LexTrack.

## 1. Tabela de Proposições (`PropositionsTable`)

### Visão Geral e Objetivo
A `PropositionsTable` exibe a lista operacional e detalhada das proposições legislativas que correspondem aos filtros de busca aplicados. Ela funciona como o ponto de partida principal para o drill-down analítico individual.

### Onde Aparece
* **Dashboard geral (`/dashboard`):** Ocupa a metade inferior da página em [dashboard-page.tsx](../../../frontend/src/pages/dashboard-page.tsx#L568-L616).
* *Nota:* Está fisicamente disponível para uso na página órfã [consulta-proposicoes-page.tsx](../../../frontend/src/pages/consulta-proposicoes-page.tsx).

### Interface TypeScript e Propriedades (Props)
Implementada em [PropositionsTable.tsx](../../../frontend/src/features/proposicoes/components/PropositionsTable.tsx):

```typescript
interface PropositionsTableProps {
  propositions: Proposition[];              // Vetor de proposições normalizadas
  onSort?: (field: string) => void;          // Callback disparado ao clicar nas colunas ordenáveis
  onPropositionClick?: (id: string) => void; // Callback disparado ao clicar em uma linha para abrir detalhes
}
```

### Colunas e Mapeamento Semântico
1. **Proposição:** Exibe o tipo, o número/ano da matéria (ex: `PL 123/2024`) e o nome do autor principal.
2. **Ementa:** Texto explicativo resumido. Utiliza a classe utilitária `.line-clamp-2` para limitar a exibição a no máximo duas linhas.
3. **Casa Atual:** Badge colorido mapeando a localização atual da matéria:
   * `Câmara`: `bg-blue-100 text-blue-800` (Azul)
   * `Senado`: `bg-purple-100 text-purple-800` (Roxo)
   * `Sanção`: `bg-emerald-100 text-emerald-800` (Verde)
4. **Fase Atual:** Etapa processual canônica atual.
5. **Dias na Etapa:** Período decorrido na fase atual de análise.
6. **Último Evento Relevante:** Descrição e data do último marco legislativo significativo.
7. **Atraso:** Dias de atraso em relação à mediana histórica do grupo. Rótulo "Crítico" em vermelho caso exceda 15 dias.
8. **Cobertura:** Barra de progresso percentual indicando a completude dos metadados individuais.
9. **Status:** Situação geral (ex: "Em Tramitação", "Arquivada").

---

## 2. Componente de Paginação (`Pagination`)

### Visão Geral e Objetivo
Componente utilitário que fornece os controles de navegação e indica a faixa de dados em exibição.

### Onde Aparece
* Acoplado à tabela principal na `DashboardPage`.

### Estrutura e Propriedades
Definido como componente compartilhado de UI em [index.tsx](../../../frontend/src/shared/ui/index.tsx#L153-L205):

```typescript
export function Pagination({ pagina, total, itensPorPagina, onChange }: {
  pagina: number;             // Página ativa atual (1-indexed)
  total: number;              // Quantidade total de registros filtrados
  itensPorPagina: number;     // Limite de registros por página (padrão: 10)
  onChange: (p: number) => void; // Callback disparado ao mudar de página
})
```

---

## 3. Problemas e Oportunidades Identificados
* **Duplicidade de Controles:** A `DashboardPage` implementa um controle de paginação simplificado e inline (linhas 591-613) que não utiliza o componente `<Pagination />` reutilizável do `shared/ui/index.tsx`.
* **Mapeamento Inline:** Os métodos de coloração de badges (`getCasaColor` e `getStatusColor`) estão codificados dentro do próprio arquivo `PropositionsTable.tsx`.
  * *Recomendação:* Mover essas funções utilitárias para a biblioteca de constantes ou helpers em `src/shared/lib/` para permitir reuso em outras telas (como na página de detalhes).

---

## 4. Arquivos Relacionados
* **Componente da Tabela:** [PropositionsTable.tsx](../../../frontend/src/features/proposicoes/components/PropositionsTable.tsx)
* **Componente de Paginação:** [shared/ui/index.tsx](../../../frontend/src/shared/ui/index.tsx#L153-L205)
