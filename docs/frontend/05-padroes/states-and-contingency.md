# Padrão de Projeto - Estados de Interface e Contingência (States & Contingency)

Este documento descreve os padrões de design de interface e implementação técnica adotados no LexTrack para gerenciar os estados de carregamento (Loading), ausência de dados (Empty State) e erros de infraestrutura (Error Fallbacks).

---

## 1. Carregamento (Loading States)
Para evitar oscilações visuais bruscas ("layout shift") e fornecer feedback imediato de atividade, o LexTrack utiliza duas estratégias principais:

### A. Skeletons (Carregamento de Estruturas Complexas)
Para componentes estruturais e tabelas, são usados blocos de "esqueleto" que piscam sutilmente com animação de pulso.
* **Dashboard (KPIs e Gráficos):** Implementado diretamente em [DashboardComponents.tsx](../../../frontend/src/features/dashboard/DashboardComponents.tsx#L33-L38):
  ```typescript
  if (loading) return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="bg-ink-800 border border-ink-700/50 rounded-xl p-5 h-28 animate-pulse" />
      ))}
    </div>
  )
  ```
* **Lista de Proposições:** Implementado em [ProposicaoCard.tsx](../../../frontend/src/features/proposicoes/ProposicaoCard.tsx#L81-L98) via `ProposicaoListaSkeleton`, que replica 5 cards simplificados com linhas cinzas simulando metadados e ementas.

### B. Spinners (Ações e Botões)
Utilizados para sinalizar processamentos atômicos em tempo de execução (como ao submeter filtros ou aguardar uma exportação):
* **No Botão:** A propriedade `loading` do componente `Button` desativa o clique do usuário e substitui o ícone ou texto por um spinner giratório (`Loader2` do `lucide-react` com `animate-spin`).
* **Spinner Centralizado:** Componente `<Spinner />` reutilizável em [index.tsx](../../../frontend/src/shared/ui/index.tsx#L111-L113) para carregamento local.

---

## 2. Ausência de Dados (Empty State)
Quando uma consulta a filtros não retorna nenhum resultado, o sistema renderiza uma interface limpa com ilustrações ou ícones descritivos.

* **Componente:** `<EmptyState />` em [index.tsx](../../../frontend/src/shared/ui/index.tsx#L116-L124).
  ```typescript
  export function EmptyState({ title, description, icon }: { title: string; description?: string; icon?: ReactNode }) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        {icon && <div className="mb-4 text-ink-500">{icon}</div>}
        <p className="text-ink-200 font-medium">{title}</p>
        {description && <p className="mt-1 text-sm text-ink-400 max-w-sm">{description}</p>}
      </div>
    )
  }
  ```
* **Caso de Uso:** Busca por filtros incondizentes na [ConsultaProposicoesPage](../../../frontend/src/pages/consulta-proposicoes-page.tsx#L62-L67).

---

## 3. Falhas e Erros (Error Fallbacks & Contingency)
A robustez contra falhas de API externa é dividida em duas camadas:

### A. Fallback de Interface com Ícone de Alerta
Se as APIs de listagem do backend falharem por timeout ou erro de servidor, o erro capturado no `catch` é repassado ao componente `EmptyState`, exibindo uma mensagem informativa em vermelho.
* **Exemplo:** [ConsultaProposicoesPage](../../../frontend/src/pages/consulta-proposicoes-page.tsx#L56-L61)
  ```typescript
  } else if (erro) {
    return (
      <EmptyState
        title="Não foi possível carregar as proposições"
        description={erro}
        icon={<AlertCircle className="w-10 h-10 text-rose-400" />}
      />
    )
  }
  ```

### B. Injeção de Dados Mockados (Contingency)
Para fins educacionais e de demonstração, se uma chamada de dados analíticos detalhados (como o histórico de fases ou eventos no `useProposicao`) falhar na camada de rede, o hook intercepta o erro e injeta as variáveis estáticas pré-definidas (`fallbackPhases`, `fallbackEvents`, `fallbackProposition`), garantindo que o dashboard de detalhes continue operável.
* **Exemplo:** [useProposicao.ts](../../../frontend/src/shared/lib/hooks/useProposicao.ts#L183-L190)
  ```typescript
  } catch (err) {
    console.error("Erro no hook useProposicao, usando dados mockados de fallback:", err);
    if (active) {
      setProposicao(fallbackProposition);
      setPhases(fallbackPhases);
      setEvents(fallbackEvents);
      setTransitSteps(fallbackTransitSteps);
    }
  }
  ```
