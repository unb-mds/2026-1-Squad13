# Auditoria de UI - Inconsistências de Código e Design System

Este documento detalha as incompatibilidades técnicas, duplicações de componentes e conflitos de estilização identificados durante o mapeamento do frontend do LexTrack.

---

## 1. Duplicação de Componentes de KPI (Métricas)
* **Inconsistência:** O projeto possui duas implementações distintas para exibir cartões de métrica no topo do dashboard:
  1. `<KPICard />` em [KPICard.tsx](../../../frontend/src/shared/components/KPICard.tsx) (PascalCase): Suporta tendências (`trend`), modo alarme crítico com borda vermelha e usa classes de cores genéricas do Tailwind (`bg-card border-border text-foreground`).
  2. `<KpiCard />` em [index.tsx](../../../frontend/src/shared/ui/index.tsx#L127-L150) (camelCase): Não possui suporte a tendências ou ícones de alerta, usa cores fixas e escuras (`bg-ink-800 border-ink-700/50 text-white`).
* **Impacto:** Confusão de legibilidade no desenvolvimento de novos módulos e perda de unidade visual nas cores de fundo em telas que misturam ambos os componentes.

---

## 2. Conflito no Mecanismo de Temas (Dark Mode vs Classes Fixas)
* **Inconsistência:** Conflito de cores padrão entre a biblioteca de UI atômica e os componentes específicos de features.
  * O viewport principal (`AppLayout`) e as páginas estruturais usam variáveis semânticas do Tailwind (`bg-background text-foreground`).
  * Os componentes básicos de UI de [index.tsx](../../../frontend/src/shared/ui/index.tsx) (ex: `Card`, `Button`, `Input`) utilizam cores escuras fixas da paleta ink (`bg-ink-800`, `border-ink-700/50`, `bg-ink-700`).
* **Impacto:** Como a classe global `.dark` não está ativada por padrão no elemento root do HTML, o corpo do layout principal se comporta como um tema claro (Light Theme), mas os componentes internos renderizam fundos escuros da paleta `ink` de forma incongruente.

---

## 3. Páginas Inativas e Roteamento Bypass
* **Inconsistência:** Arquivos físicos de páginas completas foram criados e implementados, mas suas rotas foram desabilitadas no arquivo de rotas central.
  * A rota `/proposicoes` (que deveria renderizar [consulta-proposicoes-page.tsx](../../../frontend/src/pages/consulta-proposicoes-page.tsx)) redireciona para `/dashboard`.
  * A rota `/relatorios` (que deveria renderizar [relatorios-page.tsx](../../../frontend/src/pages/relatorios-page.tsx)) também redireciona para `/dashboard`.
* **Impacto:** Acúmulo de código inútil no bundle compilado de produção (dead code), dificultando a manutenção técnica e aumentando a complexidade da estrutura de arquivos sem valor de uso real para o usuário final.

---

## 4. Duplicidades de Recursos Legados de Protótipo
* **Inconsistência:** Permanência de arquivos de fases anteriores do protótipo que foram reescritos em novos locais sem que o arquivo antigo fosse deletado:
  * **Previsão de IA:** O arquivo `CardPrevisaoIA.tsx` em `features/tramitacoes` coexiste com o componente ativo `AIInsightsCard.tsx` em `features/proposicoes/components/`.
  * **Linha do Tempo:** O arquivo `TimelineTramitacao.tsx` em `features/tramitacoes` coexiste com a timeline completa `EventTimeline.tsx` em `features/proposicoes/components/`.
* **Impacto:** Aumento do overhead de leitura para engenheiros iniciantes que tentam decifrar qual lógica de timeline ou de cards de IA devem utilizar como padrão do projeto.
