# Story Map — Portal de Monitoramento Legislativo

---

## Critério de avaliação (PoC)

| Fase        | Entregáveis obrigatórios                                                               |
| ----------- | -------------------------------------------------------------------------------------- |
| R1 (S6–S8)  | Implementação Inicial · Release Notes · Práticas XP · Pipeline CI · Linter             |
| R2 (S9–S12) | Implantação de Software · Testes Unitários ≥90% · Testes de Integração · Release Notes |

> **Princípio desta revisão:** o que não aparece na demo ao vivo ou não é coberto por teste automatizado não tem valor de entrega no contexto acadêmico. Itens que atendem apenas critérios de cobertura foram descidos de épico funcional para enabler técnico.

---

## Definição de Pronto (DoD) — mantida do v1

| Critério                                                                         |
| -------------------------------------------------------------------------------- |
| Pull request aprovado por par                                                    |
| Testes automatizados relevantes escritos e passando                              |
| Interface responsiva: ≥ 375px mobile e ≥ 1280px desktop                          |
| Sem erros críticos no console/logs                                               |
| Dados provenientes das APIs oficiais ou banco local (sem mock hardcoded visível) |
| Commits rastreáveis no GitHub                                                    |

---

## 🟢 RELEASE 1 — MVP Demonstrável (S6–S8, ~15 dias)

> **Meta:** um fluxo completo e real de ponta a ponta que a banca consegue usar ao vivo.  
> Fluxo alvo: **login → buscar proposição → ver detalhes → ver histórico de tramitação**

---

### ÉPICO 1 — Consulta de Proposições (fechar o que está aberto)

---

#### feat: ligar busca e filtros ao backend real

**Prioridade:** Alta · **Esforço estimado:** Pequeno (a maioria já existe)

##### 📝 Descrição

O frontend já consome `GET /proposicoes` com filtros. O que falta é garantir que o fluxo funcione de ponta a ponta sem depender de mock, inclusive na tela de lista vazia e de erro.

##### 🏗️ Impacto Arquitetural

- Nenhuma mudança estrutural. Ajuste de normalização de texto (lower/strip) no `SQLProposicaoRepository` e migração de `LIKE` para `ILIKE` (ou `func.lower()`) para garantir case-insensitive no PostgreSQL.
- Paginação deve descer para SQL (`LIMIT/OFFSET`) — atualmente traz todos os registros e fatia em memória.

##### ✅ Critérios de Aceitação

- [x] Busca por palavra-chave funciona com acentos e maiúsculas sem retorno vazio indevido.
- [x] Filtros cumulativos retornam apenas registros que atendem todos os critérios.
- [x] Paginação usa `LIMIT/OFFSET` no SQL — não carrega todos os registros em memória.
- [x] Tela de lista vazia exibe mensagem informativa (não tela em branco).
- [x] Testes de integração cobrem: busca vazia (400), busca com resultado, busca sem resultado, filtro combinado.

---

#### feat: endpoint GET /proposicoes/{id} e detalhe real

**Prioridade:** Alta · **Esforço estimado:** Pequeno

##### 📝 Descrição

A página de detalhe existe e está completa visualmente, mas `obterProposicao()` no frontend ainda usa mock. Precisa de um endpoint e de ligar o frontend a ele.

##### 🏗️ Impacto Arquitetural

- **Apresentação:** novo endpoint `GET /proposicoes/{id}` em `proposicao_controller.py` reutilizando `ProposicaoResponse`.
- **Infraestrutura:** `SQLProposicaoRepository.buscar_por_id(id)` já existe — só expor na camada de apresentação.
- **Frontend:** `obterProposicao()` em `api.ts` troca `PROPOSICOES_MOCK.find()` por `fetch(${API_BASE}/proposicoes/${id})`.

##### ✅ Critérios de Aceitação

- [x] `GET /proposicoes/{id}` retorna 200 com dados completos para ID existente.
- [x] Retorna 404 para ID inexistente — frontend exibe tela "não encontrado".
- [x] Campos nulos omitidos da resposta (sem `null` visível).
- [x] Link oficial abre em nova aba.
- [x] Testes de integração: ID existente, ID inexistente.


---

### ÉPICO 2 — Tramitação Básica (versão simplificada para R1)

> **Decisão de escopo:** A entidade `Tramitacao` completa fica para R2. Para R1, exibimos os dados de tramitação que já existem na entidade `Proposicao` — tempo total, status atual e flag de atraso. É honesto e demonstrável.

---

#### feat: card de tempo de tramitação com dados reais

**Prioridade:** Alta · **Esforço estimado:** Mínimo

##### 📝 Descrição

O card de "Tempo de tramitação" na página de detalhe já renderiza corretamente — ele apenas precisa receber dados reais do backend em vez do mock. Com o endpoint `GET /proposicoes/{id}` funcionando (issue acima), isso é automático.

##### ✅ Critérios de Aceitação

- [x] `tempoTotalDias` exibido com dados reais do banco.
- [x] `atraso_critico` (> 180 dias) dispara alerta visual.
- [x] Proposições em tramitação exibem tempo acumulado até hoje.

---

### ÉPICO AUTH — Autenticação Funcional para R1

> **Decisão de escopo:** Para R1, o objetivo é ter um login que funciona de verdade — não precisa de e-mail de confirmação, recuperação de senha ou bloqueio por tentativas. Isso vai para R2. O que a banca precisa ver é que existe controle de acesso real.

---

#### feat: endpoint POST /auth/login com JWT

**Prioridade:** Alta · **Esforço estimado:** Médio

##### 📝 Descrição

Criar autenticação real no backend com geração de token JWT. O frontend já tem `AuthProvider`, `LoginForm` e `PrivateRoute` prontos — só precisa de um backend que responda de verdade.

##### 🏗️ Impacto Arquitetural

- **Domínio:** entidade `Usuario` simples (id, nome, email, senha_hash).
- **Infraestrutura:** hash de senha com `bcrypt`; repositório `UsuarioRepository`.
- **Apresentação:** `POST /auth/login` retorna `{token, user}`; middleware de verificação de JWT nas rotas protegidas.
- **Frontend:** `loginApi()` em `api.ts` troca o mock por chamada real.

##### ✅ Critérios de Aceitação

- [x] `POST /auth/login` com credenciais válidas retorna token JWT.
- [x] Token inválido em rota protegida retorna 401.
- [x] Erro de credenciais retorna mensagem genérica (sem revelar qual campo está errado).
- [x] Frontend redireciona para `/dashboard` após login bem-sucedido.
- [x] Frontend redireciona para `/login` ao tentar acessar rota privada sem token.
- [x] Testes unitários na lógica de validação de credenciais.

---

#### feat: endpoint POST /usuarios/cadastro

**Prioridade:** Alta · **Esforço estimado:** Pequeno (depende de auth/login)

##### 📝 Descrição

Cadastro real no banco. Sem e-mail de confirmação para R1.

##### ✅ Critérios de Aceitação

- [x] E-mail único — retorna 409 para duplicata com mensagem clara.
- [x] Senha mínima de 8 caracteres validada no backend.
- [x] Senha armazenada como hash (nunca em texto plano).
- [x] Frontend valida 8 caracteres (corrigir o bug atual de 6).
- [x] Testes unitários na validação de senha e unicidade.

---

### ÉPICO 5-R1 — Enablers Técnicos para Release 1

---

#### chore: dados reais no banco via script de seed

**Prioridade:** Alta · **Esforço estimado:** Pequeno

##### 📝 Descrição

Para a demo da R1 funcionar, o banco precisa ter proposições reais. Um script de seed que use os adapters existentes (`CamaraAdapter`, `SenadoAdapter`) para popular o banco com dados reais é suficiente — o worker batch automático fica para R2.

##### 🛠️ Plano de Ação

- [x] Criar `backend/src/init_db.py` (ou expandir o existente) com chamada aos adapters reais.
- [x] Seed com pelo menos 20 proposições reais (mix Câmara + Senado).
- [x] Script deve usar upsert por `id` para ser idempotente.
- [x] Documentar no README como executar o seed.

---

#### chore: corrigir SenadoAdapter — campo data_ultima_movimentacao vazio

**Prioridade:** Alta · **Esforço estimado:** Mínimo

##### 📝 Descrição

`SenadoAdapter.buscar_por_id()` retorna `data_ultima_movimentacao=""` — dado errado indo pro banco silenciosamente. Precisa extrair a data da última situação de `autuacoes`.

##### ✅ Critérios de Aceitação

- [x] `data_ultima_movimentacao` populado with a data da última situação em `autuacoes[0].situacoes[-1]`.
- [x] Se campo indisponível, retornar `data_apresentacao` como fallback (não string vazia).
- [x] Teste unitário do adapter atualizado para validar o campo.


---

## 🔵 RELEASE 2 — Produto Completo (S9–S12, ~50 dias)

> **Meta:** produto com cobertura ≥90% de testes unitários, testes de integração abrangentes, autenticação completa, coleta automatizada e timeline real de tramitação.

---

### ÉPICO 2-R2 — Tramitação Completa

---

#### feat: modelo analítico EventoTramitacao e endpoint de movimentações

**Prioridade:** Alta

##### 📝 Descrição

Migrar a lógica de tramitação para o modelo analítico `EventoTramitacao`. O componente `TimelineTramitacao` no frontend já está pronto e aguardando os novos dados normalizados.

##### 🏗️ Impacto Arquitetural

- **Domínio:** entidades `EventoTramitacao`, `FaseAnalitica`, `OrgaoLegislativo` e `TipoEvento` que substituem `Tramitacao`. Funções `classificar_tipo_evento` e `determinar_fase_analitica`.
- **Infraestrutura:** `SQLEventoTramitacaoRepository`; adapters da Câmara e Senado buscando tramitações brutas.
- **Apresentação:** `GET /proposicoes/{id}/movimentacoes` retornando lista ordenada com fases analíticas.
- **Frontend:** `obterMovimentacoes()` consome nova estrutura e mapeia as fases (ex: `NA_COMISSAO`).

##### ✅ Critérios de Aceitação

- [x] Tramitações classificadas corretamente por `TipoEvento` (20 categorias normalizadas).
- [x] Tramitações recebem uma `FaseAnalitica` correspondente.
- [x] Testes unitários do domínio valendo as classificações e fases.
- [x] Endpoint integrado devolvendo lista cronológica inversa (mais recentes primeiro).

---

#### feat: métricas de atraso e classificação de status (IAR, IAF, IEI)

**Prioridade:** Alta

##### 📝 Descrição

Implementar a lógica de classificação de atraso baseada no **Índice de Atraso Relativo (IAR)**, complementada pelo **Índice de Atraso da Fase Atual (IAF)** e **Índice de Espera Improdutiva (IEI)**.

##### 🏗️ Impacto Arquitetural

- **Domínio:** Lógica de cálculo de IAR, IAF e IEI; definição de baselines (Bootstrap Seed + Dinâmico).
- **Infraestrutura:** Tabela `baseline_tramitacao` e campos de métricas na tabela `proposicao`.
- **Apresentação:** Expor status de atraso e índices nas APIs de listagem e detalhe.

##### ✅ Critérios de Aceitação

- [ ] Baselines de bootstrap carregados no banco.
- [ ] Proposições classificadas em `NO_PRAZO`, `ATENCAO`, `ATRASADA` ou `CRITICA`.
- [ ] Detalhamento explica o atraso via IAF e IEI.
- [ ] Testes unitários cobrindo os cenários de fallback de baseline.

---

#### feat: tempo por fase com dados reais

**Prioridade:** Média

##### 📝 Descrição

Cálculo de períodos de fase via `AgregarPorFaseService`. Exibição de breakdown temporal no dossiê.

##### ✅ Critérios de Aceitação

- [ ] Tempo por fase calculado a partir das tramitações reais (Issue #130).
- [x] `TimelineTramitacao` funcional no frontend.
- [ ] Exibição do tempo acumulado por fase abaixo do tempo total.

---

### ÉPICO 3-R2 — Dashboard com Dados Reais

---

#### feat: endpoints de breakdown para gráficos do dashboard

**Prioridade:** Alta

##### 📝 Descrição

Os gráficos de tempo por tipo, por comissão e distribuição por status usam dados hardcoded no frontend. Precisam de endpoints reais no backend.

##### 🏗️ Impacto Arquitetural

- **Aplicação:** métodos de agregação no `GerarRelatorioService` (ou expandir `DashboardService`).
- **Apresentação:** `GET /dashboard/por-tipo`, `GET /dashboard/por-comissao`, `GET /dashboard/por-status`.
- **Frontend:** substituir os `delay(400)` com dados fixos por chamadas reais.

##### ✅ Critérios de Aceitação

- [x] Três endpoints de breakdown implementados e testados.
- [x] Gráficos refletem dados reais do banco.
- [x] Testes unitários nos métodos de agregação.

---

#### feat: dashboard analítico de atrasos e gargalos

**Prioridade:** Alta

##### 📝 Descrição

Expandir o dashboard para refletir as métricas de atraso, permitindo visualizar o percentual de proposições atrasadas e o IEI médio.

##### ✅ Critérios de Aceitação

- [ ] Visualização agregada de `status_atraso`.
- [ ] Ranking de órgãos/fases com maior IAF mediano.
- [ ] Filtros ativos (tipo, regime, casa) recalculam baselines contextuais no dashboard.

---

#### feat: filtros ativos afetando o dashboard

**Prioridade:** Média

##### 📝 Descrição

Atualmente o dashboard sempre mostra dados globais. Deve responder aos filtros ativos (ex: filtrar por ano altera todos os indicadores).

##### ✅ Critérios de Aceitação

- [ ] `GET /dashboard/metricas` aceita os mesmos parâmetros de filtro de `/proposicoes`.
- [ ] KPIs e gráficos recalculados conforme filtros.

---

### ÉPICO AUTH-REMOVAL — Desativação do Sistema de Autenticação

---

#### chore: remover endpoints de autenticação, serviços e migrações no backend

**Prioridade:** Alta · **Esforço estimado:** Pequeno

##### 📝 Descrição

Após o feedback da professora para remover as barreiras de login e cadastro, o backend deve deixar de expor endpoints de `/auth` e remover o middleware de proteção de rotas JWT, tornando todas as rotas de proposições e dashboards públicas por padrão.

##### ✅ Critérios de Aceitação

- [ ] Endpoints de login, registro e tokens em `auth_controller` desativados ou removidos.
- [ ] Middlewares de proteção por JWT em endpoints de proposições desativados.
- [ ] Testes de autenticação obsoletos desabilitados ou adaptados para garantir funcionamento público.
- [ ] Entidades de usuário e tabela associada no banco marcadas para posterior arquivamento ou limpas do modelo SQLModel ativo.

---

#### refactor: desativar AuthProvider, login/cadastro e rotas privadas no frontend

**Prioridade:** Alta · **Esforço estimado:** Pequeno

##### 📝 Descrição

Desativar o controle de fluxo de rotas privadas protegidas no React Router. Remover ou ocultar os formulários e páginas de Login, Cadastro e Recuperação de Senha, permitindo que a aplicação inicie diretamente na página de Dashboard sem restrições.

##### ✅ Critérios de Aceitação

- [ ] Rotas em `router/index.tsx` alteradas para expor Dashboard e Dossiê sem proteção de token.
- [ ] Remover redirecionamentos para `/login` ao acessar o Dashboard sem token no localStorage.
- [ ] Ocultar ou remover telas de login, registro e recuperação de senha.
- [ ] Componentes de layout e cabeçalho ajustados para não exibir dados de sessão de usuário ou botões de logout.

---

### ÉPICO FRONT-REFAC — Interface Sóbria de Investigação

---

#### refactor: redesenhar frontend para dashboard analítico de investigação sóbrio

**Prioridade:** Alta · **Esforço estimado:** Médio

##### 📝 Descrição

Refatorar visual do frontend React para dotá-lo de uma interface densa de dados, sóbria e focada em utilidade analítica para investigadores. A paleta de cores deve ser adaptada para tons mais escuros discretos ou neutros profissionais, priorizando a legibilidade de gráficos, mapas de calor e tabelas temporais.

##### ✅ Critérios de Aceitação

- [ ] Novo layout de dashboard implementado (estética sóbria e confiável).
- [ ] Paleta de cores corporativa colorida substituída por tons neutros e profissionais.
- [ ] Foco visual aprimorado em gráficos temporais de tramitação, baselines e estatísticas de atraso.
- [ ] Componentes adaptados para visualização clara de anomalias e gargalos no fluxo de proposições.

---

### ÉPICO GOV — Governança e Equilíbrio de Commits

---

#### chore: estabelecer rotinas de pareamento e governança para equilíbrio de commits

**Prioridade:** Média · **Esforço estimado:** Pequeno

##### 📝 Descrição

Mitigar a disparidade de commits identificada pela professora definindo um acordo de trabalho com rotação de autoria nos commits, sessões regulares de programação em par e fracionamento de issues em tarefas menores e mais fáceis de integrar.

##### ✅ Critérios de Aceitação

- [ ] Documentação de diretrizes de contribuição atualizada com práticas de Pareamento (Pair Programming).
- [ ] Utilização de co-autores no Git (`Co-authored-by`) para commits realizados em dupla.
- [ ] Registro de sessões de pareamento ou tarefas menores distribuídas para membros com menor volume de commits.

---

### ÉPICO 5-R2 — Infraestrutura de Coleta Automatizada

---

#### chore: worker de coleta batch diária (Câmara + Senado)

**Prioridade:** Alta

##### 📝 Descrição

Substituir o script de seed manual por um worker Celery agendado que mantém a base atualizada automaticamente.

##### 🛠️ Plano de Ação

- [ ] Implementar método `coletar_em_lote()` em `CamaraAdapter` com paginação automática (máx. 100 itens/página).
- [ ] Implementar método `coletar_em_lote()` em `SenadoAdapter`.
- [ ] Configurar Celery Beat com schedule `0 2 * * *` (America/Sao_Paulo).
- [ ] Upsert por número canônico no repositório.
- [ ] Retry com backoff exponencial (1s → 2s → 4s) para erros 5xx.
- [ ] Log de execução em tabela dedicada (data, hora, status, contagem).
- [ ] Falha de uma fonte não interrompe a outra.

##### ✅ Verificações de Qualidade

- [ ] Testes de integração: falha total de API, falha parcial (uma fonte cai), upsert sem duplicatas.
- [ ] Linting e type-checking passando.

---

#### chore: cache Redis para métricas do dashboard

**Prioridade:** Média

##### 📝 Descrição

`DashboardService` atualmente recalcula tudo a cada request. Com volume de dados crescente, isso se torna lento.

##### 🛠️ Plano de Ação

- [ ] Configurar cliente Redis em `infrastructure/cache/redis_client.py`.
- [ ] Implementar cache-aside no `DashboardService` com TTL de 24h.
- [ ] Invalidar cache ao término bem-sucedido do batch.
- [ ] Testes: cenário de cache hit, miss e invalidação.

---

#### chore: documentar mapeamento de campos em ADR-005

**Prioridade:** Baixa

##### 📝 Descrição

ADR-005 existe mas não tem a tabela de mapeamento de campos entre APIs e entidade de domínio.

##### 🛠️ Plano de Ação

- [ ] Adicionar tabela `Campo API Câmara → Campo Domínio` na ADR-005.
- [ ] Adicionar tabela `Campo API Senado → Campo Domínio` na ADR-005.
- [ ] Garantir que `ementa`/`txtNomeMateria` esteja claramente documentado.

---

### ÉPICO 4-R2 — Inteligência Preditiva

> **Nota:** esta funcionalidade depende do volume histórico acumulado pelo batch. Implementar apenas após o worker (Enabler 5.1-R2) estar rodando com dados suficientes.

---

#### feat: estimativa de tempo de aprovação baseada em histórico

**Prioridade:** Baixa

##### 📝 Descrição

O componente `CardPrevisaoIA` no frontend está completo com disclaimer obrigatório. O backend nunca calcula `previsao_aprovacao_dias`. Implementar apenas se o threshold de 50 proposições similares for atingido.

##### ✅ Critérios de Aceitação

- [ ] Estimativa calculada apenas quando ≥ 50 proposições similares (mesmo tipo e tema) disponíveis.
- [ ] Disclaimer obrigatório sempre exibido quando há estimativa.
- [ ] Quando indisponível, informa "dados insuficientes" (sem valor zerado).
- [ ] Testes unitários validando comportamento abaixo e acima do threshold.

---

## Itens descartados desta versão

Os itens abaixo foram presentes no story map v1 mas **removidos do escopo de entrega** por não serem demonstráveis na avaliação e consumirem tempo desproporcional:

| Item                                  | Motivo                                                                                                                                           |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Identificação de gargalos (Épico 3.2) | Parcialmente coberto pelo dashboard com dados reais; o componente de relatórios existe como mock e pode ser apresentado como protótipo funcional |
| Destaque comparativo por tema/ano     | Alto esforço, baixo impacto na banca — dados do mock já demonstram o conceito                                                                    |
| E-mail de confirmação no cadastro     | Requer infra de e-mail (SMTP/SES) — sem impacto na demo, alto risco de configuração                                                              |

---

## Resumo de prioridades por release

### Release 1 — Fechar até 2026-05-27

| Issue                                             | Esforço | Dono sugerido      |
| ------------------------------------------------- | ------- | ------------------ |
| Busca/filtros com ILIKE + paginação SQL real      | Pequeno | Backend            |
| `GET /proposicoes/{id}` + frontend ligado         | Pequeno | Backend + Frontend |
| Card tempo de tramitação com dados reais          | Mínimo  | Frontend           |
| `POST /auth/login` com JWT                        | Médio   | Backend            |
| `POST /usuarios/cadastro`                         | Pequeno | Backend            |
| Corrigir bug validação senha (6→8 chars)          | Mínimo  | Frontend           |
| Corrigir `SenadoAdapter.data_ultima_movimentacao` | Mínimo  | Backend            |
| Script de seed com dados reais                    | Pequeno | Backend            |

### Release 2 — Fechar até 2026-07-06

| Issue                                          | Prioridade                    |
| ---------------------------------------------- | ----------------------------- |
| Entidade `Tramitacao` + endpoint movimentações | Alta                          |
| Endpoints de breakdown do dashboard            | Alta                          |
| Remoção de Autenticação (Backend)              | Alta                          |
| Remoção de Autenticação (Frontend)             | Alta                          |
| Refatoração Visual: Dashboard Sóbrio           | Alta                          |
| Worker batch Celery                            | Alta                          |
| Filtros afetando dashboard                     | Média                         |
| Cache Redis                                    | Média                         |
| Tempo por fase                                 | Média                         |
| Governança: Pareamento e Equilíbrio de Commits | Média                         |
| Estimativa preditiva                           | Baixa (condicional ao volume) |

