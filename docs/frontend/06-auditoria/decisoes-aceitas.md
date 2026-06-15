# Auditoria de UI - Decisões Aceitas (Baseline Visual Oficial)

Este documento congela e oficializa as decisões de design, fluxos de usuário e arquitetura de interface aceitos como o **baseline oficial** do frontend do LexTrack. Quaisquer refatorações futuras de layout ou de código de componente devem respeitar as diretrizes estabelecidas neste registro.

---

## 1. Organização Arquitetural (Feature-Based)
* **Decisão:** Manter a estrutura de pastas baseada em features (`src/features/[feature_name]/components/`) para componentes com escopo semântico de negócio e páginas sob `src/pages/`.
* **Racional:** Evita o acúmulo de dezenas de arquivos em pastas genéricas e facilita o desenvolvimento independente de novos fluxos de visualização.

---

## 2. Padrão de Duplo Filtro e Visualização da Timeline
* **Decisão:** A página de detalhes de proposições deve obrigatoriamente manter a segmentação entre a Timeline de Fases Agregadas (comportamento de colapso individual por fase) e a Timeline Detalhada de Eventos (filtros de granularidade: Resumo, Relevantes e Todos).
* **Racional:** Oferece excelente usabilidade tanto para usuários leigos (que buscam entender a duração macro das etapas) quanto para especialistas legislativos (que analisam a íntegra dos despachos e pareceres).

---

## 3. Resiliência por Injeção de Fallback Dinâmico
* **Decisão:** Os hooks de dados da camada de UI (`useDashboard` e `useProposicao`) devem capturar erros de requisições rejeitadas via `Promise.allSettled` e injetar dados mockados estruturais de contingência, em vez de falhar a renderização da tela.
* **Racional:** Garante que a aplicação permaneça 100% navegável e demonstrativa mesmo se os servidores de dados oficiais passarem por instabilidade temporária.

---

## 4. Layout Shell e Containers Limites
* **Decisão:** O container centralizado deve limitar-se à largura padrão de tela cheia com responsividade robusta para Desktop, Tablet e Mobile através de paddings flexíveis (`p-6` ou `p-4`) e animações de fade-in no carregamento das views.
* **Racional:** Mantém a interface harmoniosa, evitando esticamentos desproporcionais de gráficos e tabelas em telas ultra-wide.
