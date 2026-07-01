# Relatório Técnico Final de Encerramento e Release 2 (R2)

Este documento apresenta a retrospectiva técnica e operacional detalhada do desenvolvimento do **LexTrack** ao longo de todo o semestre letivo de 2026.1, registrando o encerramento da nossa Release 2 (R2). Redigido de forma conjunta pela nossa equipe de desenvolvimento, este relatório atua como um walkthrough minucioso dos desafios, decisões arquiteturais, algoritmos de domínio e a evolução do ecossistema de software que construímos.

O **LexTrack** é uma plataforma analítica projetada para monitorar, unificar e analisar os tempos de tramitação de proposições legislativas (Propostas de Emenda à Constituição - PECs e Projetos de Lei - PLs) na Câmara dos Deputados e no Senado Federal, fornecendo indicadores estatísticos de eficiência legislativa, detecção de gargalos burocráticos e inteligência preditiva.

---

## 1. Contexto, Equipe e Divisão de Papéis

Desenvolvemos o LexTrack como parte da disciplina de Métodos de Desenvolvimento de Software (MDS) / Engenharia de Software no primeiro semestre de 2026 (2026.1) na Universidade de Brasília (UnB) - Faculdade do Gama (FGA). 

Nossa equipe organizou-se com papéis focados, mitigando riscos de gargalos individuais e garantindo paralelismo:
* **Kaiky Santos (`kaiky-yun`):** Líder Técnico, Arquiteto de Software e DevOps Core. Liderou a modelagem do pipeline de dados, resiliência de adaptadores, motor de processamento do Gap-Filler e migrações de infraestrutura.
* **Caio Miranda (`caioflmjr`):** Líder de Frontend, Designer de Interface (UX/UI) e Quality Assurance (QA). Liderou o desenvolvimento das visualizações analíticas no frontend, a governança visual de componentes, o suporte a Dark Mode e a malha de testes unitários do frontend.
* **Heitor Barbosa (`Heitorovski01`):** Engenheiro de Dados e Analista Legislativo. Liderou a pesquisa das regras de negócio do regimento interno, a modelagem conceitual do banco de dados e auxiliou na estruturação dos classificadores.
* **Bernardo Silva (`bernardoccs1`):** Desenvolvedor Full Stack Júnior. Apoiou na refatoração de listagens, unificação de dados do dashboard e saneamento de lógicas legadas.
* **Profª. Carla Rocha (`RochaCarla`):** Orientadora do projeto e cliente primária das metas analíticas estabelecidas.

---

## 2. Linha do Tempo e Cronologia do Semestre (Walkthrough das Sprints)

Nossa jornada de desenvolvimento estendeu-se por 12 sprints semanais, divididas em três macrofases distintas:

```
[Concepção & Requisitos] (S1-S4) ──> [Release 1: MVP] (S5-S8) ──> [Release 2: Produto Completo] (S9-S12)
```

### 2.1. Concepção, Requisitos e Planejamento (Sprints 1 a 4)
* **Atividades:** Dedicamos as primeiras quatro semanas à validação do escopo do produto. Mapeamos as personas investigadoras em [personas.md](./personas.md), desenhamos a matriz de riscos e planos de mitigação em [risks.md](./risks.md), e formalizamos a Especificação de Requisitos de Software no documento [SRS.md](./SRS.md). Definimos o fluxo de valor inicial no [story-map.md](./story-map.md).

### 2.2. Release 1: Desenvolvimento do MVP (Sprints 5 a 8)
* **Atividades:** Estabelecemos a infraestrutura do monorepo e criamos a fundação da nossa arquitetura em camadas. Desenvolvemos os adaptadores básicos de comunicação com as APIs externas e expusemos os endpoints fundamentais de listagem e detalhes das proposições no backend. No frontend, implementamos a primeira versão da interface de consulta.
* **Conclusão:** A Release 1 foi encerrada com sucesso no dia **27/05/2026**, entregando as buscas cumulativas e filtros funcionais conectados a dados reais. Nossas conquistas da R1 foram consolidadas no documento [RELEASE_1_REPORT.md](./RELEASE_1_REPORT.md).

### 2.3. Release 2: O Produto Analítico Completo (Sprints 9 a 12)
* **Atividades:** A Release 2 exigiu o desenvolvimento dos motores estatísticos mais complexos do LexTrack. Construímos o modelo analítico de movimentações, a máquina de estados bicameral para transição de casas, o cálculo síncrono e batch das baselines medianas históricas, e a geração dos índices analíticos de atraso (IAR, IAF, IEI). No frontend, desenhamos um dashboard analítico consolidado e gráficos temporais interativos.
* **A Crise Financeira:** Durante esta fase, enfrentamos a expiração do *free trial* da AWS, obrigando-nos a realizar uma migração de emergência para ferramentas gratuitas de nuvem e adaptar a arquitetura em tempo recorde.
* **Conclusão:** Encerramos o desenvolvimento da Release 2 no dia **01/07/2026** (Hoje), com todos os pipelines de validação e testes em estado verde.

---

## 3. Walkthrough Detalhado da Arquitetura (ADRs)

Adotamos uma **Arquitetura em Camadas** com inversão de dependências inspirada em **Ports & Adapters (Arquitetura Hexagonal)**. O objetivo primordial foi isolar o nosso núcleo de regras de negócios (Domínio) dos detalhes de infraestrutura (APIs do Congresso Nacional, banco de dados PostgreSQL e cache do Redis).

Nossas principais decisões de arquitetura foram formalizadas em registros específicos (ADRs) na pasta [docs/adr/](./adr/):

* **[ADR-001: Layered Architecture](./adr/001-layered-architecture.md) (Sprint 5):** Escolhemos separar o código nas camadas de Apresentação, Aplicação, Domínio e Infraestrutura. Regra inegociável: dependências só apontam para baixo e a camada de Domínio é isolada de frameworks e de I/O.
* **[ADR-002: PostgreSQL](./adr/002-postgresql.md) (Sprint 5):** Decidimos usar o PostgreSQL para suportar queries analíticas complexas e funções de janela nativas, garantindo que o processamento pesado de agregação ocorra no banco, não na CPU do backend.
* **[ADR-003: FastAPI](./adr/003-fastapi.md) (Sprint 5):** Selecionamos o FastAPI para lidar com a natureza de alta concorrência de I/O nas APIs externas lentas, aproveitando a tipagem forte do Pydantic para validação na borda da aplicação.
* **[ADR-004: Batch Coleta](./adr/004-batch-coleta.md) (Sprint 5):** Para contornar a lentidão severa e indisponibilidade crônica das APIs da Câmara e do Senado, estabelecemos que a busca de dados seria síncrona em banco de dados local. A sincronização ocorre em lote agendado (batch diário às 02:00 BRT).
* **[ADR-005: Padrão Adapter](./adr/005-adapter-pattern.md) (Sprint 5):** Criamos adaptadores de infraestrutura atuando como uma camada anticorrupção (*Anti-Corruption Layer - ACL*). Eles convertem dados heterogêneos de APIs em entidades canônicas do domínio.
* **[ADR-006: Redis Cache](./adr/006-redis-cache.md) (Sprint 6):** Introduzimos o Redis para cachear os agregados analíticos mais lentos do dashboard, invalidando o cache de forma reativa a cada coleta diária concluída.
* **[ADR-007: Estratégia de Testes](./adr/007-testing-strategy.md) (Sprint 7):** Definimos a automação com `pytest` (backend) e `vitest` + `React Testing Library` (frontend), exigindo o isolamento de chamadas de rede externas.
* **[ADR-008: GitHub Actions](./adr/008-github-actions-pipeline-dados.md) (Sprint 8):** Criamos a rotina de exportação estática de dados para o Squad Dashboard via Actions para proteger nossas chaves de acesso.
* **[ADR-009: Squad Dashboard Standalone](./adr/009-squad-dashboard-standalone.md) (Sprint 8):** Decidimos que o Squad Dashboard seria uma aplicação estática React independente, hospedada de forma gratuita no GitHub Pages.
* **[ADR-010: Separação de Status](./adr/010-status-normalization.md) (Sprint 9):** Dividimos a representação das proposições em `status` (campo canônico curto e normalizado para indexação de busca e filtros) e `status_original` (texto bruto detalhado fornecido pelo órgão de origem).
* **[ADR-012: Governança Frontend](./adr/012-governanca-frontend.md) (Sprint 10):** Normatizamos padrões visuais, checklists em PRs de tela, uso do operador `Promise.allSettled` para otimizar tempo de carregamento da interface e Dark Mode centralizado.
* **[ADR-013: Estimativa de Tempo LLM](./adr/013-llm-time-estimation.md) (Sprint 11):** Adotamos a integração com o modelo de linguagem gratuito Gemini 1.5 Flash para atuar como estimador auxiliar, encapsulado em uma porta de infraestrutura e protegido por cache do Redis para não estourar os limites de requisições gratuitas (15 RPM).

---

## 4. O Pipeline de Ingestão e Processamento de Dados ( walkthrough Técnico)

Mapeamos a seguir o pipeline fim a fim que concebemos para processar as informações legislativas brasileiras:

### 4.1. Coleta e Resiliência
Quando disparada, a nossa rotina de coleta síncrona aciona dois adaptadores na camada de infraestrutura:
* **`CamaraAdapter`:** Executa chamadas HTTP síncronas paralelas à API de Dados Abertos da Câmara. Buscamos de forma simultânea o detalhe da proposição, seus autores, o histórico de tramitações e as proposições apensadas ou relacionadas. Limitamos a concorrência a 15 conexões.
* **`SenadoAdapter`:** A API do Senado Federal funciona sobre chamadas XML aninhadas, por vezes gerando indisponibilidade em requisições de emendas. O adaptador do Senado foi projetado para ler a estrutura de Matérias e fallbacks para Processos. Limitamos a concorrência a 5 conexões.
* **Mecanismos de Defesa:** Implementamos políticas automáticas de re-tentativa (*retry*) com recuo exponencial e limites variáveis de timeout da requisição. Caso a API do Senado de emendas fique indisponível, registramos uma chave temporária no Redis habilitando degradação seletiva (o sistema continua coletando o projeto e suas tramitações normais, ignorando o processamento de emendas por 15 minutos para não interromper a transação do banco).

### 4.2. Normalização Regimental e Mapeamento de Fases
Convertemos os dados brutos e descrições livres das movimentações legislativas para as nossas 20 categorias de `TipoEvento` e as 8 fases do `FaseCodigo`.

#### As 8 Fases Analíticas do LexTrack:
Nossa modelagem mapeia as fases fundamentais da tramitação de leis com base no Regimento Interno da Câmara (RICD) e na Constituição Federal de 1988 (CF88):
1. **`PROTOCOLO_INICIAL`** (RICD, Art. 102): Numeração inicial e leitura do projeto na mesa diretora.
2. **`ANALISE_COMISSOES`** (RICD, Arts. 120 e 121): Trâmite temático nas comissões de mérito ou na CCJ.
3. **`AGUARDANDO_PAUTA`** (RICD, Art. 124): Projetos com pareceres prontos aguardando despacho da Presidência da Casa para inserção na Ordem do Dia.
4. **`DELIBERACAO_PLENARIO`** (RICD, Arts. 120 a 124): Fase de debate e escrutínio dos votos em Plenário.
5. **`TRAMITE_ENTRE_CASAS`** (CF88, Art. 65): Processo de envio físico e registro digital de envio da Casa Iniciadora para a Casa Revisora.
6. **`REVISAO_OUTRA_CASA`** (CF88, Art. 65): Trâmite do projeto sob análise do Senado (se iniciado na Câmara) ou vice-versa.
7. **`ETAPA_EXECUTIVO`** (CF88, Art. 66): Prazo constitucional de 15 dias úteis para sanção ou veto presidencial do autógrafo.
8. **`ENCERRADA`** (CF88, Art. 66): Estado terminal (Sancionado/Promulgado ou Rejeitado/Arquivado).

#### Expressões Regulares de Classificação (Regex):
Implementamos 17 padrões de expressões regulares com prioridade de cima para baixo. Destacamos o regex defensivo de **`APRESENTACAO`**:
```regex
(?<!requerimento\s)(apresentaç\|leitura)(?!\sde\srequerimento)
```
* **Nossa Justificativa:** As tramitações estão repletas de movimentações contendo a leitura ou apresentação de "requerimentos acessórios" ordinários (ex. requerimento de urgência, requerimento de audiência pública). Sem o lookbehind e o lookahead negativos que inserimos, a nossa máquina de estados (FSM) classificaria erroneamente a leitura de um requerimento como uma nova "Apresentação do Projeto Principal", forçando o sistema a regredir indevidamente a proposição da fase de Comissões ou Plenário para o `PROTOCOLO_INICIAL`.

### 4.3. Algoritmo FSM de Trânsito entre Casas
Concebemos uma Máquina de Estados Finito (FSM) no domínio para rastrear a movimentação bicameral das proposições:
* **Entradas de Transição:** Mapeamos gatilhos de `GATILHO_REMESSA` e `GATILHO_RETORNO` detectados por termos e órgãos da movimentação.
* **Nossos Estados de Trânsito:** O sistema armazena a casa de origem da proposição e computa o estado de `TransitStep` contendo a casa onde o projeto se encontra ativamente (Câmara ou Senado), seu papel (Iniciadora, Revisora ou Retorno), data de entrada, data de saída e a duração exata daquele passo.
* **Prevenção de Ping-Pong:** Incluímos uma regra invariante de segurança que bloqueia cascades de correções retroativas de fuso horário ou lançamentos em duplicidade pelas APIs, impedindo transições implícitas que desestabilizem a integridade das datas de trâmite registradas.

### 4.4. Crossover e Deduplicação Bicameral
Quando um projeto tramita entre Câmara e Senado, ele gera históricos duplicados e logs concorrentes em ambos os portais legislativos. Para criar uma timeline limpa e integrada, desenvolvemos a lógica de crossover no `ListarMovimentacoesService`:
1. **União Cronológica:** Fundimos a lista de eventos de ambos os adaptadores em uma única coleção e ordenamos pelo timestamp `data_evento` de forma ascendente.
2. **Deduplicação Semântica:** Eventos equivalentes ocorrem com diferença de poucos minutos. Eliminamos redundâncias computando uma assinatura MD5 ou chave de string baseada na data reduzida a minutos e nos primeiros 50 caracteres da descrição original em caixa baixa:
   $$\text{Chave} = (\text{data\_evento}[:16], \text{descricao\_original}[:50].\text{lower}())$$
   Caso a assinatura já conste na partição do conjunto unificado, o registro duplicado é descartado.
3. **Reindexação:** Geramos um novo índice de `sequencia` sequencial e unificado do primeiro ao último evento do histórico composto.

### 4.5. Heurística de Apensamento
Para rastrear dependências de proposições-filho anexadas a proposições-pai, desenvolvemos um extrator por regex:
```regex
([A-Z]{2,3})\s*(\d+)/(\d{4})
```
Quando o classificador detecta um evento do tipo `APENSAMENTO`, extraímos a sigla do tipo, o número e o ano da proposição principal referenciada no log de texto (ex: "PL 221/2019"). Se o projeto principal já existir em nosso banco de dados, estabelecemos o vínculo físico de dependência e gravamos a relação na tabela `apensamento` com uma pontuação de confiança de **`0.9` (90%)**, usada pelo frontend para gerar os alertas de bloqueio na interface.

---

## 5. Walkthrough Detalhado do Motor do Gap-Filler

O preenchimento adaptativo de lacunas de dados (Gap-Filler) é um dos nossos componentes de engenharia mais sofisticados, projetado para operar sob restrições severas de infraestrutura em ambiente de produção:

1. **Vigilância de Cobertura (Scouting):**
   * Avaliamos ciclicamente a diferença entre a contagem de proposições salvas localmente vs. o total disponível nas APIs oficiais do Congresso para cada ano fiscal e tipo de documento.
   * Se um ano possui integridade $\ge 99.5\%$, salvamos este estado permanentemente no Redis para ignorá-lo em varreduras futuras (*Pruning*), poupando requisições desnecessárias.
   * Se a cobertura for inferior a $95\%$, registramos o ano e tipo como uma "lacuna ativa".
2. **Prevenção de Sobreposição por Lock Distribuído:**
   * Protegemos a execução diária com uma trava distribuída no Redis (`seeding:lock:task_executando`) usando a operação atômica `SET NX` com tempo de expiração para impedir que instâncias paralelas de workers executem a mesma rotina de varredura.
   * Para gerenciar o cursor da página que está sendo processada, os workers realizam transações otimistas no Redis com a estratégia `WATCH/MULTI/EXEC` sobre a chave `seeding:cursor:{fonte}:{ano}:{tipo}`, evitando que workers leiam a mesma fatia de dados das APIs.
3. **Algoritmo Concorrente Adaptativo (AIMD + RTT):**
   Para proteger o servidor de banimentos de IP e quedas de serviço, implementamos um controle dinâmico inspirado em redes TCP: **AIMD (Additive Increase / Multiplicative Decrease)**:
   * Monitoramos continuamente o tempo de resposta médio das requisições externas ($P95$ RTT).
   * **Se saudável (sem erros de rede & latência baixa):** Incrementamos aditivamente o tamanho do lote de coleta ($+20$ proposições) e liberamos conexões concorrentes no semáforo ($+1$).
   * **Se HTTP 429 (Rate Limit) ou Timeout:** Efetuamos corte multiplicativo de $50\%$ no limite concorrente do semáforo e no volume máximo de proposições da fila do lote.
   * **Se HTTP 5xx (Server Error):** Aplicamos recuo preventivo de $25\%$ nas variáveis de concorrência.
4. **Circuit Breaker de Coleta:**
   * Caso a incidência de erros de requisição (HTTP 429 ou 503) ultrapasse $20\%$ em um único lote, abrimos o disjuntor lógico (`seeding:circuit_breaker:{fonte}:estado` $\to$ `OPEN`) por 30 minutos, suspendendo temporariamente todas as buscas do Gap-Filler daquela fonte para poupar o nosso IP.

---

## 6. Algoritmos de Métricas e Calibração de Baselines

Concebemos três métricas analíticas principais no domínio para analisar os tempos de processamento do Congresso Nacional:

### 6.1. Equações Estatísticas
* **Índice de Atraso Relativo (IAR):**
  $$IAR = \frac{\text{Dias Decorridos Totais}}{\text{Mediana Histórica Esperada (\text{Grupo Equivalente})}}$$
  Classificamos as matérias legislativas com base no comportamento de controle: *No Prazo* ($IAR < 1.0$), *Atenção* ($1.0 \le IAR < 1.5$), *Atrasada* ($1.5 \le IAR < 2.5$) ou *Crítica* ($IAR \ge 2.5$).
* **Índice de Atraso da Fase Atual (IAF):**
  $$IAF = \frac{\text{Dias Gastos na Fase Atual}}{\text{Mediana Histórica da Fase (\text{Grupo Equivalente})}}$$
  Computamos este índice unicamente para proposições ativas (não arquivadas ou promulgadas), sinalizando qual fase analítica específica está concentrando a retenção temporal corrente.
* **Índice de Espera Improdutiva (IEI):**
  $$IEI = \frac{\text{Dias em Eventos Não-Deliberativos}}{\text{Dias Decorridos Totais}}$$
  Representa a inércia burocrática. Varremos o histórico de eventos da proposição acumulando o tempo gasto entre movimentações que não alteram a fase, não alteram o órgão deliberativo e não são classificadas como deliberativas.

### 6.2. Calibração Estatística e Bootstrap Seeds
O recálculo das medianas históricas exige volume de dados representativo ($n \ge 30$ proposições concluídas com a mesma combinação de tipo e regime de tramitação). Para evitar falhas em partidas a frio (cold start) ou sob escassez de dados, definimos baselines fixas de segurança (**Bootstrap Seeds**):
* **Projetos de Lei (PL) Ordinários:** Mediana de 730 dias (2 anos).
* **Projetos de Lei (PL) em Regime de Urgência:** Mediana de 90 dias.
* **Propostas de Emenda à Constituição (PEC) Ordinárias:** Mediana de 1095 dias (3 anos).
* **Medida Provisória (MPV):** Mediana de 60 dias (tempo regulamentar de vigência constitucional).
* **Fase ANALISE_COMISSOES (PL Ordinário):** Mediana de 180 dias.
* **Fase ETAPA_EXECUTIVO:** Mediana de 15 dias úteis.

---

## 7. O Grande Desafio: O Fim do Trial da AWS e a Transição para Nuvem "Free Tier"

Na metade do desenvolvimento da Release 2, o período de testes gratuitos (*free trial*) de nossa conta dedicada na AWS expirou de forma súbita. Isso nos forçou a desenhar uma nova estratégia de deploy e infraestrutura em produção sem estourar o nosso orçamento (custo zero).

Mapeamos a seguir a nossa migração e as soluções de engenharia adotadas:

### 7.1. Readequação de Provedores
* **Frontend:** Migrado da nossa VM antiga para a plataforma **Vercel**, configurando CD automático no GitHub Actions para fazer build de produção do monorepo a cada push em `develop`/`main`.
* **Backend:** Hospedado no plano gratuito do **Render** (limitação severa de 512 MB de RAM por container e spin-down de inatividade).
* **Banco de Dados:** Hospedado na camada de banco de dados gratuito do **Supabase** (PostgreSQL).

### 7.2. Contornando as Limitações de Instâncias Gratuitas

#### Substituição do Celery Workers por GitHub Actions Crons
A hospedagem gratuita do Render não nos permite rodar múltiplos contêineres e processos ativos em background de forma persistente (o que impossibilita termos contêineres dedicados para Redis, Celery Workers e Celery Beat ativos sem custos).

* **Nossa Solução:** Mantivemos o Celery, Redis e workers assíncronos no ambiente de desenvolvimento local dos desenvolvedores (via comandos do docker-compose local). Para a produção em nuvem, expusemos as rotinas internas do backend FastAPI sob rotas HTTP internas de controle:
  * `/internal/tarefas/coleta` (Orquestra a coleta incremental e preenchimento de lacunas).
  * `/internal/tarefas/baselines` (Orquestra o recálculo diário das medianas históricas).
  * `/internal/tarefas/metricas` (Orquestra o cálculo analítico de IAR, IAF, IEI de todas as proposições).
* **Segurança:** Protegemos essas rotas usando o middleware `internal_auth.py`, que exige o cabeçalho HTTP `X-Internal-Token` correspondente a um segredo criptográfico forte cadastrado como segredo do repositório.
* **Orquestração via Crons do GitHub Actions:** Criamos workflows agendados do GitHub Actions (`cron-coleta.yml`, `cron-baselines.yml` e `cron-metricas.yml`) que usam comandos `curl` estruturados contra o backend no Render, disparados em horários encadeados (02:37, 03:00 e 04:00 BRT diariamente).

#### Mitigação de Out Of Memory (OOM) no Render
A limitação física de **512 MB de RAM** no Render resultava em travamento da máquina e morte do container (*OOM*) ao rodar buscas síncronas de mais de 30 proposições concorrentes (devido ao acúmulo de XMLs volumosos de tramitações e emendas na memória do Python).

* **Nossa Solução:** Reduzimos a nossa variável `COTA_GLOBAL_MAX` de **40 para 20 proposições** por requisição da API de coleta incremental, garantindo que o consumo do processo não exceda o limite de RAM do Render. Complementamos com o aumento do tempo de timeout do `curl` no GitHub Actions para 300 segundos, permitindo que a requisição seja concluída de forma segura mesmo se a instância gratuita do Render sofrer com picos de latência ou spin-up de inatividade.

#### Otimização de Pool de Banco de Dados no Supabase
O plano do Supabase gratuito limita o número de conexões simultâneas que o PostgreSQL aceita.
* **Nossa Solução:** Ajustamos o pool do SQLAlchemy no arquivo `infrastructure/database/__init__.py` para reciclar conexões inativas mais rapidamente e passamos a envelopar todas as sessões em blocos de contexto `with` ou blocos `try/finally` explícitos, eliminando conexões zumbis que travavam o banco de produção.

---

## 8. Garantia de Qualidade (QA) e Cobertura de Testes

Nossa malha de testes evoluiu de forma expressiva ao longo do semestre:
* **Início do Projeto:** Começamos o repositório com zero testes funcionais.
* **Estado Final (R2 Concluída):** Estabelecemos uma cobertura total de **523+ casos de teste** integrados que rodam de forma automática a cada Pull Request em nosso pipeline de integração contínua (CI):
  * **425 testes de backend** no `pytest` cobrindo detalhadamente a lógica de FSM, algoritmos de cálculo de métricas de atraso, o motor do Gap-Filler adaptativo com trava do Redis e repositórios SQL.
  * **10 arquivos de suítes de teste de frontend** no `vitest` e `React Testing Library` (com 64 casos de teste internos) cobrindo componentes cruciais da interface (como o `<ProposicaoCard />` e o `<ThemeToggle />`), hooks de debounce e a rigorosa camada de mappers de propriedades (`mappers.ts`) que traduz variáveis do backend (`snake_case`) para propriedades do React (`camelCase`).

---

## 9. Bugs Críticos Resolvidos no Semestre

### 9.1. Colisão de Chaves Primárias no Postgres
* **O Bug:** As APIs da Câmara e do Senado geram IDs sequenciais numéricos que colidem (ex: ambas possuem proposições com ID `24500`). Salvar esses dados na mesma tabela do nosso banco gerava sobreposição e erro de chave primária.
* **Nossa Resolução:** Alteramos a modelagem de banco para exigir IDs com prefixo de origem (`camara:{id}` e `senado:{id}`). Criamos o script de migração de dados **`update_ids_migration.py`** que desabilita temporariamente as chaves estrangeiras (`session_replication_role = 'replica'`) para injetar retroativamente a prefixação em todas as tabelas de proposição, movimentações e apensamentos do banco de dados em produção.

### 9.2. Erro de Parser no `SenadoAdapter`
* **O Bug:** O `SenadoAdapter` falhava silenciosamente e salvava o campo `data_ultima_movimentacao` como string vazia `""` para proposições antigas, quebrando os cálculos analíticos de inatividade.
* **Nossa Resolução:** Refatoramos a lógica do adaptador para buscar a data a partir do campo regimental `DataSituacao` das autuações, fazendo fallback automático para a `data_apresentacao` se o campo de tramitação atual estivesse vazio.

### 9.3. Bloqueio por Chamada Inválida de Emendas na Câmara
* **O Bug:** A Câmara depreciou o endpoint direto de emendas, fazendo com que as chamadas do adaptador retornassem erro `HTTP 405 Method Not Allowed`, ocultando o número de emendas de todas as matérias.
* **Nossa Resolução:** Migramos a requisição do adaptador para consultar o endpoint `/relacionadas` e filtrar registros do tipo `EM` (emenda) ou `SBT` (substitutivo). Lançamos a migração Alembic `b3f102f30e6g_reset_numero_emendas_to_null.py` e rodamos o serviço `BackfillEmendasService` para atualizar as contagens retroativamente com integridade.

---

## 10. Governança do Frontend e Backlog Técnico

Durante o encerramento da Release 2, identificamos oportunidades de refatoração que foram registradas em nosso backlog de débito técnico para futura manutenção:

### 10.1. Inventário de Componentes de KPIs Coexistentes
Identificamos a coexistência de dois componentes de cartões no frontend que não foram unificados em tempo hábil para a R2:
* **`<KPICard />`:** Usado exclusivamente no Dashboard principal. Possui suporte nativo a ícones de tendência, modo de alerta em vermelho (`isAlarm`) e tooltips informativos carregados com metadados explicativos.
* **`<MetricCard />`:** Usado exclusivamente na página de detalhes da proposição. Versão simplificada voltada a dados individuais de trâmite, utilizando o atributo HTML nativo `title` para explicações.
* *Nota de Governança:* O componente duplicado `<KpiCard />` (camelCase) foi permanentemente removido por redundância.

### 10.2. Arquivamento de Rotas e Páginas Órfãs
Com a desativação do fluxo de login e cadastro na R2 (ADR-010), redirecionamos as rotas órfãs para a página do Dashboard para proteger o fluxo do usuário. Os seguintes arquivos permanecem no repositório como histórico técnico de desenvolvimento:
* `consulta-proposicoes-page.tsx` (antiga rota `/proposicoes` - as consultas foram unificadas na tela inicial).
* `relatorios-page.tsx` (antiga rota `/relatorios` - as visualizações de gargalos foram embarcadas como widget de comissões).
* As issues de controle de autenticação (#86, #92, #93) foram catalogadas para encerramento permanente.
