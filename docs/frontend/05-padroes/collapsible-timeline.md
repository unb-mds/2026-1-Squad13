# Padrão de Projeto - Timelines Colapsáveis e Fluxos de Tramitação

Este documento especifica a arquitetura e comportamento interativo dos componentes de linha do tempo (timeline) na página de detalhes da proposição, detalhando a agregação por fases e o histórico granular de eventos.

---

## 1. Visão Geral
A análise temporal do trâmite legislativo é segmentada em duas visões complementares:
1. **Timeline de Fases Agregadas (`PhaseTimeline`):** Visão macroscópica que divide a trajetória em etapas formais e seus respectivos períodos de permanência.
2. **Timeline de Eventos Granulares (`EventTimeline`):** Visão microscópica com o histórico sequencial de despachos, pareceres, deliberações e emendas emitidos pelas comissões e plenários.

---

## 2. Timeline de Fases Agregadas (`PhaseTimeline`)
Este componente agrupa a tramitação em macroperíodos cronológicos. Cada bloco representa o tempo contínuo que a proposição permaneceu sob a jurisdição de um determinado órgão ou estágio.

* **Local do Código:** [PhaseTimeline.tsx](../../../frontend/src/features/proposicoes/components/PhaseTimeline.tsx)

### A. Funcionalidades e Comportamento Visual
* **Colapsável/Expansível:** Cada fase possui um estado local (`expandedPhases`) controlado por clique. Ao expandir, o usuário visualiza:
  * Data exata de entrada e saída (ou indicação de "Em andamento" na cor primária se for a fase atual).
  * Informações de atraso em dias em comparação com a mediana histórica.
  * Alerta visual chamativo para **Atraso Crítico** (acima de 15 dias).
* **Fase Ativa (Corrente):** Destacada com borda esquerda larga na cor primária (`border-l-4 border-primary`) e fundo com opacidade sutil (`bg-primary/5`).
* **Indicador de Recorrência:** Sinaliza com um ícone de rotação (`RotateCcw`) e um Badge amarelo se a proposição retornou à mesma comissão ou etapa mais de uma vez (ex: `2ª vez`).
* **Conexão Visual:** Uma linha vertical tracejada (`absolute left-6 w-0.5 bg-border`) conecta as bolhas indicadoras das fases subsequentes, exceto no último item do vetor.

---

## 3. Timeline de Eventos Granulares (`EventTimeline`)
Exibe a totalidade dos despachos oficiais e ações executadas. Como o volume de eventos de uma proposição antiga pode ser muito extenso, este componente adota estratégias de filtragem de ruído.

* **Local do Código:** [EventTimeline.tsx](../../../frontend/src/features/proposicoes/components/EventTimeline.tsx)

### A. Comportamento e Navegação
* **Header Colapsável Geral:** O histórico detalhado inicia-se minimizado em formato de sumário informativo (exibindo quantidade de marcos, trânsitos e atrasos detectados) para economizar espaço de tela. Clicar no header expande a lista completa.
* **Filtros Locais de Visualização:**
  * **Resumo:** Exibe apenas eventos canônicos ou cruciais (mudanças de fase, deliberações em comissões, pareceres e atrasos).
  * **Relevantes:** Filtra por eventos marcados como `isRelevante = true` pelo backend.
  * **Todos:** Exibe a lista exaustiva de movimentações registradas na API.

### B. Mapeamento Semântico e Ícones
Os eventos são categorizados visualmente de acordo com a sua tipagem (`tipoEvento`), mudando as cores de fundo e os ícones correspondentes:

| Tipo de Evento | Ícone (Lucide) | Cores CSS (Tailwind) | Significado Semântico |
| :--- | :--- | :--- | :--- |
| `mudanca-fase` | `ArrowRightLeft` | `text-primary bg-primary/10` | Entrada em nova comissão ou fase de análise |
| `deliberacao` | `CheckCircle2` | `text-emerald-600 bg-emerald-50` | Votações de relatórios ou substitutivos |
| `apensamento` | `Link2` | `text-amber-600 bg-amber-50` | Junção de proposições correlatas |
| `transicao-casa` | `ArrowRightLeft` | `text-purple-600 bg-purple-50` | Envio da Câmara para o Senado (ou vice-versa) |
| `parecer` / outros | `FileText` | `text-muted-foreground bg-muted` | Emissão de pareceres técnicos, despachos simples |

---

## 4. Integração de Dados e Mappers
Os dados vindos do backend (API oficial da Câmara e Senado) são adaptados na camada de domínio da aplicação antes de alimentar os componentes de timeline.
* O mapeamento é definido em [mappers.ts](../../../frontend/src/shared/lib/mappers.ts#L113-L125), que analisa o histórico de movimentações para classificar os tipos de evento analítico (`mudanca-fase`, `deliberacao`, etc.) e atribuir as respectivas bandeiras de controle (`flags`).
