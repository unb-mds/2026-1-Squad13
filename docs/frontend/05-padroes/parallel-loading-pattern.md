# Padrão de Projeto - Carregamento Paralelo Resiliente (Parallel Loading Pattern)

Este documento descreve o padrão de carregamento paralelo assíncrono adotado no LexTrack para otimizar o tempo de resposta e garantir resiliência da interface de usuário perante falhas parciais em APIs de dados legislativos.

---

## 1. Contexto e Motivação
A página de Dashboard e a página de Detalhes da Proposição necessitam de dados agregados de múltiplas fontes e endpoints distintos (métricas agregadas, tempos de fase, gargalos de análise, cobertura de metadados, série histórica temporal, etc.).

Se fôssemos carregar cada requisição sequencialmente (usando `await` linha após linha), introduziríamos um gargalo linear de latência: o tempo total de carregamento seria a soma do tempo de todas as chamadas (`T_total = t1 + t2 + ... + tn`). 

O carregamento paralelo reduz esse tempo para o tempo da chamada mais lenta (`T_total = max(t1, t2, ..., tn)`).

---

## 2. Escolha Estrutural: `Promise.allSettled` vs `Promise.all`
Tradicionalmente, desenvolvedores utilizam `Promise.all` para requisições paralelas. Porém, o `Promise.all` adota uma política de "tudo ou nada" (fast-fail): se uma única requisição falhar (rejeitar), a promessa inteira falha imediatamente, descartando os resultados que obtiveram sucesso.

No LexTrack, devido à instabilidade e variabilidade inerente às APIs externas (Câmara/Senado) integradas na camada de infraestrutura do backend, adota-se **`Promise.allSettled`**:
1. **Resiliência Parcial:** Se a requisição de "Evolução Temporal" falhar, o usuário ainda conseguirá visualizar os cards de KPIs de volumetria e o gráfico de status.
2. **Desacoplamento de Erro:** Os erros de carregamento são isolados e tratados individualmente por módulo, permitindo carregar dados mockados ou exibir estados vazios (`empty states`) sem quebrar a tela inteira.

---

## 3. Implementação Prática

### A. Exemplo 1: Dashboard (`useDashboard`)
No hook [useDashboard.ts](../../../frontend/src/shared/lib/hooks/useDashboard.ts#L105-L114), as APIs de estatísticas e gráficos são chamadas em paralelo:

```typescript
const [
  metricasRes,
  tempoFaseRes,
  gargalosRes,
  temasRes,
  statusRes,
  evolucaoRes,
  transicoesRes,
  coberturaRes
] = await Promise.allSettled([
  obterMetricas(filtros),
  obterTempoPorFase(filtros),
  obterGargalos(filtros),
  obterComparacaoTemas(filtros),
  obterDadosStatus(filtros),
  obterEvolucaoTemporal(filtros),
  obterTransicoesCasas(filtros),
  obterCoberturaDados(filtros)
]);
```

#### Tratamento de Resultados e Fallbacks
Para cada resposta retornada no array, o código verifica o status do resultado (`fulfilled` ou `rejected`) antes de atualizar o estado da aplicação:

```typescript
// Exemplo de sucesso: atualiza estado ativo
if (metricasRes.status === "fulfilled" && metricasRes.value) {
  setMetricas(metricasRes.value);
}

// Exemplo de fallback: se falhar, utiliza os dados mockados pré-definidos
if (coberturaRes.status === "fulfilled" && coberturaRes.value) {
  setCoberturaData(coberturaRes.value);
} else {
  setCoberturaData(defaultCoberturaData); // Fallback silencioso
}
```

---

### B. Exemplo 2: Detalhe da Proposição (`useProposicao`)
No hook [useProposicao.ts](../../../frontend/src/shared/lib/hooks/useProposicao.ts#L137-L141), o carregamento de fases de tramitação e logs detalhados de eventos ocorre em paralelo:

```typescript
const [fasesRes, eventosRes, reliabilityRes] = await Promise.allSettled([
  obterMovimentacoesFases(propId),
  obterMovimentacoesEventos(propId, "relevante"),
  obterConfiabilidade(propId)
]);
```

* Se o backend não responder a tempo sobre as fases de tramitação (`fasesRes.status === 'rejected'`), o componente de timeline de fases (`PhaseTimeline`) realiza um fallback automático para o mock estrutural de fases (`fallbackPhases`), mantendo a página funcional e interativa para estudo pedagógico do usuário.

---

## 4. Regras para Novas Implementações
Ao adicionar novas páginas ou blocos de dados integrados a APIs:
1. **Nunca use `Promise.all` diretamente** para requisições de renderização de múltiplos blocos independentes de tela. Use sempre `Promise.allSettled`.
2. **Defina dados de contingência (fallbacks):** Sempre declare objetos padrão (mocks coerentes com o layout) para serem injetados em caso de rejeição da promessa correspondente.
3. **Gerenciamento de Ciclo de Vida (`active` flag):** Sempre inclua uma variável booleana de controle (ex: `let active = true;`) dentro do `useEffect` para evitar vazamentos de memória e race conditions (chamar `setState` de componente desmontado).
