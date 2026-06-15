# Especificação de Arquitetura de Frontend e UX

## Sistema de Monitoramento Legislativo Federal

Este documento define a arquitetura de frontend, os princípios de UX, a organização de telas, os componentes de domínio e as diretrizes visuais para um sistema analítico de monitoramento da tramitação de proposições legislativas federais. O objetivo é transformar um backend já robusto — capaz de normalizar eventos heterogêneos da Câmara dos Deputados e do Senado Federal em uma linha do tempo analítica unificada — em uma experiência de produto coesa, legível, institucional e orientada à investigação de fluxo legislativo.[cite:16][cite:20]

O sistema não deve ser tratado como um dashboard genérico de BI, nem como um portal passivo de consulta legislativa. Seu encaixe correto é o de um dashboard analítico de fluxo legislativo, com capacidades de observabilidade processual, drill-down por proposição, explicabilidade de métricas e leitura operacional de gargalos, permanência, trânsito entre casas e confiabilidade dos dados.[cite:16][cite:19]

A base arquitetural do backend sustenta essa direção ao fornecer fases canônicas, classificação de eventos, detecção de atraso, relevância de eventos, agregação por períodos de fase, controle de recorrência cíclica e unificação cross-over entre Câmara e Senado, além de graceful degradation quando fontes externas falham.[cite:18]

## Objetivos do frontend

O frontend deve cumprir simultaneamente cinco objetivos centrais:

- Traduzir a complexidade do domínio legislativo em uma interface compreensível e navegável.[cite:19]
- Tornar visíveis métricas de fluxo, espera, atraso, permanência, encerramento e trânsito entre casas.[cite:16][cite:19]
- Oferecer exploração progressiva, saindo do panorama institucional para o caso individual de cada proposição.[cite:20]
- Comunicar claramente cobertura, parcialidade e confiabilidade dos dados exibidos, dado o contexto de instabilidade das APIs externas.[cite:18]
- Materializar visualmente a robustez do backend, evitando que a camada de apresentação pareça genérica ou desconectada do domínio.[cite:20]

Em termos de produto, a pergunta principal que a interface deve responder é: “como está fluindo a tramitação das proposições monitoradas, onde estão os gargalos e quais casos merecem investigação imediata?”.[cite:16][cite:19]

## Posicionamento do produto

O sistema deve ser entendido como um produto de civic tech analítico, com caráter híbrido entre:

- Dashboard de performance parlamentar.
- Sistema de legislative tracking.
- Interface de observabilidade de processo público.

Essa combinação é a mais aderente porque o domínio não pede apenas visualização estática de indicadores, mas acompanhamento do comportamento dinâmico das proposições ao longo do tempo, em múltiplas fases, órgãos e casas legislativas.[cite:16][cite:19]

Portanto, o frontend deve adotar linguagem de produto analítico, não de portal institucional clássico. Ao mesmo tempo, deve evitar o visual excessivamente comercial de ferramentas SaaS genéricas, privilegiando sobriedade, legibilidade, rastreabilidade e confiança.

## Princípios de UX

### 1. Legibilidade antes de ornamentação

A prioridade visual deve ser a leitura rápida de estado, fase, atraso, confiabilidade e trânsito. Elementos decorativos só devem existir quando contribuírem para reforçar hierarquia, semântica ou navegação.

### 2. Explicabilidade do dado

Toda métrica sensível ao domínio deve poder ser explicada. Termos como “atraso”, “evento relevante”, “cobertura”, “fase atual” e “tempo mediano” não devem aparecer como rótulos opacos; devem ser acompanhados por tooltip, ajuda contextual, nota de rodapé visual ou microcopy de apoio.[cite:18][cite:19]

### 3. Overview primeiro, detalhe depois

A navegação deve seguir uma progressão clara:

1. Panorama do sistema.
2. Fluxo e distribuição.
3. Gargalos e padrões.
4. Lista operacional de proposições.
5. Detalhe individual da proposição.

Esse fluxo reduz carga cognitiva e se alinha ao objetivo do projeto, que combina leitura macro do processo com investigação pontual de casos.[cite:16][cite:20]

### 4. Consistência semântica

Fases, status, cobertura e criticidade devem manter o mesmo significado visual em todas as telas. Se “Análise em Comissões” usa determinada cor, ordem e ícone na dashboard, deve manter esse mesmo sistema na tabela, na timeline e no detalhe.

### 5. Confiabilidade visível

Como a base pode ser parcial em função de falhas nas APIs externas, o sistema deve exibir claramente nível de cobertura, modo de fallback, última atualização e escopo da amostra. A confiança na interface depende tanto da qualidade do dado quanto da honestidade com que suas limitações são comunicadas.[cite:18]

### 6. Investigação sem fricção

O sistema deve reduzir o caminho entre detectar anomalia e investigar causa. Isso significa filtros persistentes, links diretos entre dashboard e tabelas, drill-down previsível e breadcrumbs claros entre visão geral e detalhe.

## Perfis de usuário

Embora o projeto seja acadêmico, a arquitetura de frontend deve supor pelo menos quatro perfis de uso:

| Perfil | Objetivo principal | Necessidades de UX |
|---|---|---|
| Professor/avaliador | Entender rapidamente o valor do sistema | Tela inicial forte, métricas claras, narrativa visual coerente |
| Analista de políticas públicas | Investigar desempenho e gargalos | Filtros, comparações, ranking, leitura temporal |
| Usuário cívico interessado | Explorar proposições e entender fluxo | Linguagem acessível, tooltips, timeline clara |
| Desenvolvedor do projeto | Implementar e evoluir a interface | Componentização consistente e arquitetura previsível |

## Arquitetura de informação

A estrutura principal do produto deve ser organizada em cinco áreas:

### 1. Dashboard geral

Tela de entrada do sistema. Responde ao estado agregado do ecossistema monitorado.

Perguntas que deve responder:
- Quantas proposições estão monitoradas?
- Quantas estão ativas, encerradas ou em atraso?
- Em quais fases elas se concentram?
- Como o fluxo evolui no tempo?
- Onde estão os principais gargalos?

### 2. Proposições

Tela analítica de listagem. Deve funcionar como camada operacional e investigativa.

Perguntas que deve responder:
- Quais proposições merecem atenção imediata?
- Quais estão com maior tempo parado?
- Quais possuem dados parciais?
- Quais estão em determinada fase, órgão, casa ou tema?

### 3. Detalhe da proposição

Tela de investigação profunda. É onde a normalização do backend se materializa com mais força.

Perguntas que deve responder:
- Qual é o estado atual da matéria?
- Por quais fases ela passou?
- Quantas vezes retornou a uma fase?
- Quais eventos foram considerados relevantes?
- Onde houve atraso ou inércia?
- Houve trânsito entre Câmara e Senado?

### 4. Gargalos e padrões

Tela comparativa e diagnóstica. Pode ser uma área independente ou uma subseção avançada da dashboard principal.

Perguntas que deve responder:
- Quais órgãos concentram maior permanência?
- Quais fases acumulam mais atraso?
- Quais temas ou tipos estão mais lentos?
- Qual casa apresenta maior inércia em determinados recortes?

### 5. Metadados e confiabilidade

Área de apoio transversal. Pode aparecer em drawer, painel lateral, footer expandido ou cartões específicos.

Perguntas que deve responder:
- Qual é a fonte dos dados?
- Quando foram atualizados?
- O histórico está completo ou parcial?
- Há fallback local ativo?
- O cruzamento entre casas foi bem-sucedido?

## Mapa de telas

| Tela | Papel | Prioridade |
|---|---|---|
| Dashboard geral | Visão executiva e analítica do sistema | Muito alta |
| Lista de proposições | Operação e triagem | Muito alta |
| Detalhe da proposição | Investigação e narrativa do caso | Muito alta |
| Gargalos e padrões | Diagnóstico comparativo | Alta |
| Configurações/ajuda metodológica | Transparência conceitual | Média |

## Dashboard geral

### Estrutura da tela

A dashboard principal deve ser organizada verticalmente em blocos lógicos, com leitura de cima para baixo:

1. Header global.
2. Linha de filtros.
3. KPIs principais.
4. Pipeline de tramitação legislativa.
5. Trânsito entre casas.
6. Evolução temporal e cobertura dos dados.
7. Bloco de gargalos.
8. Tabela resumida de proposições em análise.

Essa ordem é adequada porque respeita a progressão cognitiva do usuário: primeiro contexto, depois estado, depois fluxo, depois explicação, depois investigação.[cite:16][cite:20]

### Header global

O header deve conter:

- Nome do produto.
- Busca por proposição.
- Controle de período global.
- Ações secundárias, como exportar ou abrir ajuda metodológica.
- Indicador de atualização de dados.

O header não deve ser visualmente pesado. Seu papel é orientar navegação, não competir com os indicadores centrais.

### Filtros globais

Filtros recomendados:

- Casa: Câmara, Senado, ambas.
- Tipo: PL, PEC e outros tipos suportados.
- Tema.
- Fase atual.
- Status de atraso.
- Cobertura: completa, parcial, fallback.
- Faixa temporal.

Regras de UX para filtros:
- Devem ter persistência visível na mesma sessão.
- Devem refletir imediatamente sobre KPIs, gráficos e tabela, salvo se a equipe decidir por um botão explícito de aplicar filtros.
- Devem exibir chips ativos de forma clara.
- Deve existir ação de limpar todos.

### KPIs principais

A primeira linha de KPIs deve trazer métricas de leitura instantânea:

- Total de proposições monitoradas.
- Proposições ativas.
- Proposições em atraso.
- Tempo mediano de tramitação.
- Proporção com histórico unificado entre casas.

Cada KPI deve conter:
- Valor principal.
- Subtexto explicativo.
- Tooltip metodológico opcional.
- Variação temporal quando aplicável.

Os KPIs não devem ser numerosos. Entre quatro e seis é o intervalo mais seguro para preservar escaneabilidade.

### Pipeline de tramitação

Esse é o centro semântico da dashboard. Deve representar as 8 fases canônicas do sistema:

1. Protocolo inicial.
2. Análise em comissões.
3. Aguardando pauta.
4. Deliberação em plenário.
5. Trâmite entre casas.
6. Revisão na outra casa.
7. Etapa do executivo.
8. Encerrada.[cite:18]

Para cada fase, o componente pode mostrar:
- Quantidade de proposições na fase.
- Percentual sobre o total filtrado.
- Tempo mediano na fase.
- Número de casos em atraso.

Regras de UX:
- A ordem deve ser fixa e corresponder ao modelo analítico do domínio.
- O clique em uma fase deve filtrar toda a tela.
- A fase atual selecionada deve ficar claramente destacada.
- A cor da fase deve ser discreta e reutilizada em outras telas.

### Trânsito entre casas

Esse bloco é uma assinatura do produto e precisa aparecer com mais protagonismo que em dashboards comuns. O backend já possui lógica de remessa, recebimento, retorno à casa iniciadora e unificação cross-over, o que justifica transformar esse aspecto em um componente visual próprio.[cite:18]

Elementos sugeridos:
- Total de proposições em trânsito no momento.
- Quantidade atualmente na Câmara e no Senado.
- Quantidade retornada à casa iniciadora.
- Mini fluxo visual Câmara  Senado  retorno, com contadores.

Esse bloco deve ser visualmente diagramático. Mais do que um card, ele deve parecer um mapa resumido do deslocamento entre casas.

### Evolução temporal

Deve responder como o fluxo muda ao longo do tempo.

Visualizações recomendadas:
- Linha de entradas e saídas por período.
- Evolução do tempo mediano de tramitação.
- Volume de proposições em atraso ao longo do tempo.

Boas práticas:
- Evitar excesso de séries no mesmo gráfico.
- Permitir trocar métrica exibida por tabs ou segmented control.
- Usar legenda simples e tooltip rico.

### Cobertura dos dados

A cobertura de dados não deve ser tratada como detalhe invisível. Como a confiabilidade é parte estrutural do produto, o ideal é que exista um bloco próprio com:

- Percentual de histórico completo.
- Percentual de histórico parcial.
- Percentual proveniente de fallback/persistência local.
- Nota explicando impacto analítico.[cite:18]

Esse componente ajuda o usuário a interpretar corretamente os resultados e evita falsa impressão de completude.

### Gargalos

O bloco de gargalos deve priorizar leitura comparativa.

Recortes possíveis:
- Top órgãos com maior permanência mediana.
- Fases com maior incidência de atraso.
- Temas mais lentos.
- Tipos de proposição com maior inércia.

Regras:
- Apresentar ranking simples e clicável.
- Oferecer troca de recorte por tabs.
- Mostrar valor e contexto, não apenas ordinal.

### Tabela resumida

A parte inferior da dashboard deve trazer uma amostra operacional de proposições em análise detalhada.

Colunas recomendadas:
- Identificador da proposição.
- Ementa resumida.
- Casa atual.
- Fase atual.
- Dias na etapa.
- Último evento relevante.
- Nível de atraso.
- Cobertura.
- Ação de abrir detalhe.

Essa tabela é a ponte entre visão geral e investigação de caso.[cite:16][cite:20]

## Tela de proposições

A tela de proposições deve ser uma visão mais extensa da tabela da dashboard, com recursos de exploração avançada.

### Objetivos

- Triar proposições problemáticas.
- Comparar casos dentro de um recorte.
- Aplicar filtros compostos.
- Abrir rapidamente o detalhe de cada matéria.

### Elementos essenciais

- Cabeçalho com total filtrado.
- Filtros laterais ou superiores.
- Tabela principal com ordenação por coluna.
- Busca textual.
- Paginação ou virtualização.
- Exportação opcional.

### Colunas prioritárias

| Coluna | Justificativa |
|---|---|
| Proposição | Identificação do caso |
| Tipo | Classificação legislativa |
| Tema | Recorte analítico |
| Casa atual | Estado institucional atual |
| Fase atual | Estado analítico atual |
| Dias na etapa | Medida operacional central |
| Último evento relevante | Contexto de andamento |
| Atraso | Criticidade |
| Cobertura | Qualidade do dado |
| Atualizado em | Rastreabilidade |

### Interações importantes

- Ordenar por dias na etapa, atraso, atualização e fase.
- Filtrar por múltiplos critérios simultaneamente.
- Salvar visões filtradas em memória de sessão, se desejado.
- Abrir detalhe por clique na linha inteira, além de ação explícita.

## Tela de detalhe da proposição

Essa é a tela mais importante para expressar a força do backend. Ela deve transformar a linha do tempo normalizada em uma narrativa visual clara e investigável.[cite:20][cite:18]

### Estrutura recomendada

1. Cabeçalho da proposição.
2. Resumo do estado atual.
3. Linha do tempo resumida por fases.
4. Linha do tempo detalhada por eventos relevantes.
5. Blocos analíticos laterais ou inferiores.
6. Painel de confiabilidade e observações.

### Cabeçalho da proposição

Deve conter:
- Identificador completo.
- Ementa.
- Tipo.
- Tema.
- Casa atual.
- Fase atual.
- Status de atraso.
- Indicador de cobertura.

### Resumo do estado atual

Cards resumidos:
- Dias totais acumulados.
- Dias na etapa atual.
- Número de fases percorridas.
- Número de eventos relevantes.
- Quantidade de retornos/recorrências de fase.

### Timeline por fases

Essa timeline deve usar os períodos agregados por fase, e não apenas eventos crus. Isso se alinha ao modo resumido e à lógica de PeriodoFase suportada pelo backend.[cite:18]

Cada fase deve mostrar:
- Nome da fase.
- Ocorrência (ex.: ocorrência 2 em análise em comissões).
- Data de entrada e saída.
- Duração.
- Indicador de atraso, quando aplicável.

### Timeline por eventos relevantes

A timeline detalhada deve listar apenas eventos relevantes por padrão, com opção de expandir para histórico completo. Isso reduz ruído e valoriza a modelagem analítica definida no domínio.[cite:18][cite:19]

Cada evento deve mostrar:
- Data e hora.
- Tipo de evento canônico.
- Descrição original.
- Órgão.
- Se mudou fase.
- Se foi deliberativo.
- Se marcou atraso.
- Se envolveu apensamento.

### Blocos analíticos complementares

Sugestões:
- Distribuição do tempo por fase.
- Eventos que mais impactaram o ciclo.
- Histórico de trânsito entre casas.
- Relações de apensamento, quando existirem.

### Painel de confiabilidade

Esse painel deve explicar:
- Se houve coleta nas duas casas.
- Se houve fallback local.
- Se o histórico é parcial.
- Última sincronização.
- Observações metodológicas relevantes.

## Tela de gargalos e padrões

Essa tela deve oferecer leitura transversal do sistema.

### Blocos sugeridos

- Ranking por órgão/comissão.
- Ranking por fase.
- Heatmap fase x tema.
- Comparação Câmara x Senado.
- Série temporal de acúmulo de atraso.

### Regras de UX

- Um recorte principal por vez.
- Alternância simples entre eixos de comparação.
- Contexto textual curto sobre o que está sendo medido.
- Clique nos rankings deve abrir lista de proposições correspondentes.

## Sistema de componentes

O frontend deve ser construído a partir de um design system leve, porém fortemente semântico.

### Componentes de domínio

#### PhaseBadge

Representa fase analítica. Deve conter nome, cor semântica e opção de ícone discreto.

#### DelayIndicator

Representa criticidade temporal. Deve suportar ao menos três estados:
- Dentro do esperado.
- Atenção.
- Em atraso.

#### CoverageBadge

Representa completude e origem do dado:
- Completo.
- Parcial.
- Fallback local.

#### HouseTransitionChip

Representa movimento entre Câmara e Senado:
- Remessa.
- Recebimento.
- Retorno.

#### EventFlag

Representa atributos do evento:
- Relevante.
- Deliberativo.
- Mudou fase.
- Apensamento.

#### TimelineEventCard

Componente base para exibir eventos da trilha detalhada.

#### PropositionRow

Linha reutilizável da tabela analítica, adaptável para dashboard e listagem completa.

## Linguagem visual

### Direção estética

A linguagem visual deve ser institucional-contemporânea, com equilíbrio entre autoridade pública e clareza de produto analítico. O sistema não deve parecer antiquado, mas tampouco deve adotar estéticas de startup futurista, gradientes chamativos ou exagero decorativo.

### Cores

Sugestão de lógica cromática:
- Fundo neutro claro ou grafite em dark mode.
- Cor primária: azul-petróleo ou verde-azulado profundo.
- Cores semânticas discretas para fases.
- Amarelo/laranja para atenção.
- Vermelho controlado para atraso crítico.
- Verde apenas quando a semântica exigir, evitando comunicação enganosa de “sucesso”.

### Tipografia

A tipografia deve priorizar legibilidade em tabelas, métricas e labels densos. Uma família sans séria e contemporânea é a melhor escolha para esse contexto.

### Ícones

Ícones devem ser simples, lineares e funcionais. Seu papel principal é reforçar estado ou ação, não decorar.

## Estados de interface

Todo componente de dados deve prever pelo menos estes estados:

- Carregando.
- Vazio.
- Erro.
- Parcial.
- Atualizado com sucesso.

### Skeletons

A dashboard deve ter skeletons estruturais para KPIs, gráficos, ranking e tabela. Skeleton deve espelhar o layout real e não apenas blocos genéricos.

### Estado vazio

Estados vazios devem ser explicativos e orientados à ação. Exemplo: “Nenhuma proposição corresponde aos filtros atuais”.

### Estado parcial

Esse estado é especialmente importante neste produto. Ele deve explicar que o resultado foi gerado com cobertura parcial ou fallback local, sem impedir a continuidade da análise.[cite:18]

### Estado de erro

Erros não devem expor detalhes técnicos crus. Devem informar se o problema veio de indisponibilidade externa, falha interna ou ausência temporária de atualização.

## Navegação

### Estrutura sugerida

- Dashboard
- Proposições
- Gargalos
- Metodologia

A tela de detalhe da proposição entra como rota de profundidade, não como item fixo de navegação principal.

### Breadcrumbs

No detalhe, deve existir breadcrumb explícito, por exemplo:

Dashboard / Proposições / PL 123/2024

Isso preserva contexto durante a investigação.

## Regras de interação

- Cards clicáveis devem ter hover discreto e foco claro.
- Toda ação importante deve ter feedback visível.
- Filtros aplicados devem ser facilmente removíveis.
- Tabelas devem ter cabeçalho fixo em cenários de scroll mais longo.
- Tooltips devem ser curtos, conceituais e não bloquear leitura.

## Responsividade

Mesmo sendo um sistema analítico, a interface deve funcionar em resoluções menores.

### Desktop

É o formato primário. Deve concentrar dashboard completa, tabela ampla e comparações paralelas.

### Tablet

Pode reorganizar cards e reduzir densidade lateral.

### Mobile

No mobile, a prioridade deve ser:
- KPIs.
- Filtros básicos.
- Lista resumida.
- Acesso ao detalhe.

Gráficos complexos e tabelas densas podem virar cards empilhados, abas ou visualizações resumidas.

## Acessibilidade

Diretrizes mínimas:

- Contraste adequado para texto e badges.
- Navegação por teclado.
- Labels claros para filtros e busca.
- Ícones nunca devem carregar significado sozinhos.
- Estados de atraso e cobertura não podem depender apenas de cor.

## Arquitetura técnica sugerida para o frontend

Considerando o stack já adotado pelo projeto, a arquitetura pode seguir uma organização em React com separação por domínio, componentes, features e páginas.[cite:17]

### Estrutura sugerida

```text
src/
  app/
    router/
    providers/
    layout/
  pages/
    dashboard/
    proposicoes/
    proposicao-detalhe/
    gargalos/
    metodologia/
  features/
    filtros/
    metricas/
    pipeline/
    timeline/
    cobertura/
    gargalos/
    proposicoes/
  entities/
    proposicao/
    evento/
    fase/
  shared/
    ui/
    hooks/
    lib/
    types/
    constants/
```

### Princípios arquiteturais

- Separar componentes visuais de regras de composição de tela.
- Centralizar contratos de dados tipados vindos da API.
- Isolar transformações de view-model quando necessário.
- Evitar acoplamento entre tabela, dashboard e detalhe.
- Reaproveitar componentes de domínio em múltiplas telas.

## Contratos de exibição

Cada recurso de backend importante deve ter uma tradução explícita no frontend:

| Recurso de backend | Tradução no frontend |
|---|---|
| Fase canônica | PhaseBadge, pipeline, timeline por fase |
| Evento relevante | TimelineEventCard, destaque visual |
| diasNaEtapa | DelayIndicator, ranking, tabela |
| temAtraso | Badge, filtro, prioridade visual |
| remessaOuRetorno | HouseTransitionChip, mapa de trânsito |
| PeriodoFase | Timeline resumida |
| Cobertura parcial/fallback | CoverageBadge, painel de confiabilidade |
| Ocorrência cíclica | Marcador de recorrência |

## Métricas prioritárias de frontend

A primeira versão do produto deve priorizar métricas que já possuem aderência conceitual forte com o modelo de domínio:

- Total monitorado.
- Ativas vs encerradas.
- Em atraso.
- Tempo mediano de tramitação.
- Dias na etapa atual.
- Tempo por fase.
- Distribuição por fase.
- Trânsito entre casas.
- Gargalos por órgão e tema.

## Microcopy

O sistema deve usar microcopy clara, curta e orientada a explicação.

Exemplos:
- “Em atraso” em vez de “status crítico”.
- “Cobertura parcial” em vez de “dados incompletos”.
- “Último evento relevante” em vez de “última movimentação válida”.
- “Tempo mediano na fase” em vez de “tempo central agregado”.

## Roadmap de prototipação

### Fase 1

Congelar a dashboard principal com base no wireframe refinado já explorado visualmente.

### Fase 2

Projetar a tela de proposições como continuação operacional da dashboard.

### Fase 3

Projetar o detalhe da proposição como peça central de demonstração da robustez do backend.

### Fase 4

Consolidar design system mínimo: badges, chips, cards, tabelas, timeline, tooltips.

### Fase 5

Transformar protótipos em componentes React reais.

## Critérios de qualidade

A arquitetura de frontend será considerada bem-sucedida quando:

- A dashboard responder claramente às principais perguntas analíticas do sistema.[cite:16][cite:19]
- A listagem permitir investigação e priorização operacional.[cite:16]
- O detalhe da proposição demonstrar com clareza a normalização e a linha do tempo analítica.[cite:20][cite:18]
- A interface comunicar honestamente cobertura e confiabilidade dos dados.[cite:18]
- A experiência visual parecer própria, coerente e aderente ao domínio legislativo.
- O frontend conseguir espelhar a robustez do backend, em vez de simplificá-lo excessivamente.[cite:20]

## Conclusão

A principal missão deste frontend não é apenas “mostrar dados”, mas traduzir uma arquitetura analítica complexa em uma experiência investigativa, clara e institucionalmente confiável. O valor do produto nasce justamente do encontro entre um backend que normaliza o caos legislativo e um frontend que transforma essa inteligência em compreensão, triagem e narrativa visual.[cite:20][cite:18]

Por isso, a arquitetura proposta deve ser lida como uma extensão direta do domínio, e não como uma camada decorativa sobre ele. Quando bem implementado, o frontend passa a funcionar como a manifestação visível da máquina analítica construída no backend: fases, eventos, relevância, atraso, trânsito, cobertura e recorrência deixam de ser abstrações técnicas e passam a ser instrumentos de leitura pública do processo legislativo.[cite:19][cite:20]
