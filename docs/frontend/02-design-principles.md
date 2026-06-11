# 02 - Princípios de Design e UX

Este documento descreve os princípios de Usabilidade (UX) e as diretrizes estéticas que orientam o desenvolvimento e a revisão da interface do LexTrack.

## Contexto de Produto (Civic Tech)
O LexTrack não deve ser tratado como um painel genérico de BI corporativo ou um portal governamental estático. Ele se posiciona como um **sistema de observabilidade legislativa de interesse público**. 
A interface deve priorizar sobriedade, rigor analítico, rastreabilidade técnica dos dados e transparência conceitual sobre ornamentações estéticas ou efeitos dinâmicos excessivos.

---

## Princípios de Experiência do Usuário (UX)

### 1. Clareza Analítica antes de Estética
* **Regra:** Elementos visuais (linhas, cores, ícones) só devem ser inseridos se cumprirem um papel informativo claro.
* **Aplicação:** Evitamos gradientes chamativos e decorações tridimensionais. Cores são semânticas e os espaçamentos são pensados para acomodar textos longos (como ementas).

### 2. Explicabilidade Contextual dos Dados
* **Regra:** Toda métrica complexa ou indicador estatístico de domínio deve ser autoexplicativo no contexto da tela.
* **Aplicação:** Conceitos como "Atraso Crítico", "Confiabilidade", "Tempo Mediano" e "Cobertura de Dados" são sempre acompanhados de tooltips informativos (como o [InfoTooltip](./04-componentes/forms-and-inputs.md) e microcopies de apoio).

### 3. Progressive Disclosure (Exploração Progressiva)
* **Regra:** O fluxo de navegação deve guiar o usuário do panorama macro para o detalhe atômico de maneira previsível.
* **Aplicação:**
  1. *Visão Geral:* KPIs consolidados do ecossistema legislativo no topo do dashboard.
  2. *Fluxo de Processo:* Distribuição de proposições no pipeline.
  3. *Análise de Gargalos:* Rankings e gráficos transversais (órgãos, temas).
  4. *Operação:* Tabela operacional com filtros avançados.
  5. *Investigação:* Drill-down profundo na página de detalhe da proposição.

### 4. Consistência Semântica de Cores e Ícones
* **Regra:** Um mesmo estado de processo ou indicador deve manter a mesma representação visual em todas as views.
* **Aplicação:** Se a situação "Aprovada" é colorida com tons de verde (`bg-emerald-100` ou similar) no dashboard, ela deve manter rigorosamente o mesmo padrão de cor e estilo nas linhas da tabela e na timeline de eventos.

### 5. Transparência da Integridade do Dado (Observabilidade de Rede)
* **Regra:** Falhas de coleta, dados parciais ou fallbacks de rede causados por instabilidades de APIs governamentais devem ser honestamente exibidos ao usuário.
* **Aplicação:** O indicador de **Cobertura de Dados** ocupa local de destaque nas telas, e avisos metodológicos explicam a composição da amostra estatística.

---

## Diretrizes de Acessibilidade (Acessibilidade Mínima)
* **Contraste de Cor:** As cores de badges e textos devem obedecer a relações de contraste legíveis (WCAG AA).
* **Navegação por Teclado:** Elementos interativos (inputs de busca, selects, botões de paginação) devem possuir estados focáveis claros (`focus:ring-2 focus:ring-primary`).
* **Não Dependência Exclusiva de Cores:** Indicadores de atraso crítico nunca transmitem informação apenas por cores (ex: vermelho/verde); sempre adicionamos rótulos textuais de status (ex: "Crítico", "+45d").

---

## Próximos Passos recomendados para Leitura
* Para conferir os tokens de cores e fontes definidos no sistema, leia o [Design Tokens](./03-design-tokens.md).
* Para compreender a implementação física de botões e seletores que respeitam estes princípios, consulte o catálogo de [Componentes de Formulário](./04-componentes/forms-and-inputs.md).
