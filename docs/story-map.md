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

- [ ] Busca por palavra-chave funciona com acentos e maiúsculas sem retorno vazio indevido.
- [ ] Filtros cumulativos retornam apenas registros que atendem todos os critérios.
- [ ] Paginação usa `LIMIT/OFFSET` no SQL — não carrega todos os registros em memória.
- [ ] Tela de lista vazia exibe mensagem informativa (não tela em branco).
- [ ] Testes de integração cobrem: busca vazia (400), busca com resultado, busca sem resultado, filtro combinado.

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

- [ ] `GET /proposicoes/{id}` retorna 200 com dados completos para ID existente.
- [ ] Retorna 404 para ID inexistente — frontend exibe tela "não encontrado".
- [ ] Campos nulos omitidos da resposta (sem `null` visível).
- [ ] Link oficial abre em nova aba.
- [ ] Testes de integração: ID existente, ID inexistente.

---

### ÉPICO 2 — Tramitação Básica (versão simplificada para R1)

> **Decisão de escopo:** A entidade `Tramitacao` completa fica para R2. Para R1, exibimos os dados de tramitação que já existem na entidade `Proposicao` — tempo total, status atual e flag de atraso. É honesto e demonstrável.

---

#### feat: card de tempo de tramitação com dados reais

**Prioridade:** Alta · **Esforço estimado:** Mínimo

##### 📝 Descrição

O card de "Tempo de tramitação" na página de detalhe já renderiza corretamente — ele apenas precisa receber dados reais do backend em vez do mock. Com o endpoint `GET /proposicoes/{id}` funcionando (issue acima), isso é automático.

##### ✅ Critérios de Aceitação

- [ ] `tempoTotalDias` exibido com dados reais do banco.
- [ ] `atraso_critico` (> 180 dias) dispara alerta visual.
- [ ] Proposições em tramitação exibem tempo acumulado até hoje.

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

- [ ] `POST /auth/login` com credenciais válidas retorna token JWT.
- [ ] Token inválido em rota protegida retorna 401.
- [ ] Erro de credenciais retorna mensagem genérica (sem revelar qual campo está errado).
- [ ] Frontend redireciona para `/dashboard` após login bem-sucedido.
- [ ] Frontend redireciona para `/login` ao tentar acessar rota privada sem token.
- [ ] Testes unitários na lógica de validação de credenciais.

---

#### feat: endpoint POST /usuarios/cadastro

**Prioridade:** Alta · **Esforço estimado:** Pequeno (depende de auth/login)

##### 📝 Descrição

Cadastro real no banco. Sem e-mail de confirmação para R1.

##### ✅ Critérios de Aceitação

- [ ] E-mail único — retorna 409 para duplicata com mensagem clara.
- [ ] Senha mínima de 8 caracteres validada no backend.
- [ ] Senha armazenada como hash (nunca em texto plano).
- [ ] Frontend valida 8 caracteres (corrigir o bug atual de 6).
- [ ] Testes unitários na validação de senha e unicidade.

---

### ÉPICO 5-R1 — Enablers Técnicos para Release 1

---

#### chore: dados reais no banco via script de seed

**Prioridade:** Alta · **Esforço estimado:** Pequeno

##### 📝 Descrição

Para a demo da R1 funcionar, o banco precisa ter proposições reais. Um script de seed que use os adapters existentes (`CamaraAdapter`, `SenadoAdapter`) para popular o banco com dados reais é suficiente — o worker batch automático fica para R2.

##### 🛠️ Plano de Ação

- [ ] Criar `backend/src/init_db.py` (ou expandir o existente) com chamada aos adapters reais.
- [ ] Seed com pelo menos 20 proposições reais (mix Câmara + Senado).
- [ ] Script deve usar upsert por `id` para ser idempotente.
- [ ] Documentar no README como executar o seed.

---

#### chore: corrigir SenadoAdapter — campo data_ultima_movimentacao vazio

**Prioridade:** Alta · **Esforço estimado:** Mínimo

##### 📝 Descrição

`SenadoAdapter.buscar_por_id()` retorna `data_ultima_movimentacao=""` — dado errado indo pro banco silenciosamente. Precisa extrair a data da última situação de `autuacoes`.

##### ✅ Critérios de Aceitação

- [ ] `data_ultima_movimentacao` populado com a data da última situação em `autuacoes[0].situacoes[-1]`.
- [ ] Se campo indisponível, retornar `data_apresentacao` como fallback (não string vazia).
- [ ] Teste unitário do adapter atualizado para validar o campo.

---

## 🔵 RELEASE 2 — Produto Completo (S9–S12, ~50 dias)

> **Meta:** produto com cobertura ≥90% de testes unitários, testes de integração abrangentes, autenticação completa, coleta automatizada e timeline real de tramitação.

---

### ÉPICO 2-R2 — Tramitação Completa

---

#### feat: entidade Tramitacao e endpoint de movimentações

**Prioridade:** Alta

##### 📝 Descrição

Criar a entidade `Tramitacao` no domínio e expor um endpoint de movimentações por proposição. O componente `TimelineTramitacao` no frontend já está pronto e aguardando dados reais.

##### 🏗️ Impacto Arquitetural

- **Domínio:** entidade `Tramitacao` com campos: `id`, `proposicao_id`, `descricao`, `orgao`, `data_entrada`, `data_saida`, `responsavel`. Método `dias_na_etapa()` como property.
- **Infraestrutura:** `TramitacaoRepository`; adapters da Câmara e Senado devem buscar tramitações junto com a proposição.
- **Apresentação:** `GET /proposicoes/{id}/movimentacoes` retornando lista ordenada.
- **Frontend:** `obterMovimentacoes()` em `api.ts` troca mock por chamada real.

##### ✅ Critérios de Aceitação

- [ ] Tramitações ordenadas da mais recente para a mais antiga.
- [ ] Cada etapa exibe: descrição, órgão, data entrada, data saída, dias calculados.
- [ ] Etapas sem data saída exibem tempo acumulado até hoje.
- [ ] Etapas > 180 dias disparam flag `tem_atraso = true`.
- [ ] Testes unitários em `dias_na_etapa()`.
- [ ] Testes de integração no endpoint.

---

#### feat: tempo por fase com dados reais

**Prioridade:** Média

##### 📝 Descrição

Com `Tramitacao` existindo, o breakdown de tempo por fase/comissão na página de detalhe pode ser calculado e exibido.

##### ✅ Critérios de Aceitação

- [ ] Tempo por fase calculado a partir das tramitações reais.
- [ ] Exibido abaixo do tempo total no dossiê.
- [ ] Somente exibido quando há dados suficientes (≥ 2 tramitações).

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

- [ ] Três endpoints de breakdown implementados e testados.
- [ ] Gráficos refletem dados reais do banco.
- [ ] Testes unitários nos métodos de agregação.

---

#### feat: filtros ativos afetando o dashboard

**Prioridade:** Média

##### 📝 Descrição

Atualmente o dashboard sempre mostra dados globais. Deve responder aos filtros ativos (ex: filtrar por ano altera todos os indicadores).

##### ✅ Critérios de Aceitação

- [ ] `GET /dashboard/metricas` aceita os mesmos parâmetros de filtro de `/proposicoes`.
- [ ] KPIs e gráficos recalculados conforme filtros.

---

### ÉPICO AUTH-R2 — Autenticação Completa

---

#### feat: logout com invalidação de token no servidor

**Prioridade:** Alta

##### 📝 Descrição

Atualmente o logout apenas limpa o localStorage — o token continua válido no servidor. Precisa de uma blacklist de tokens (Redis ou tabela no banco).

##### ✅ Critérios de Aceitação

- [ ] `POST /auth/logout` invalida o token imediatamente no servidor.
- [ ] Token invalidado retorna 401 em qualquer rota protegida subsequente.
- [ ] Botão voltar do navegador não restaura sessão após logout.

---

#### feat: recuperação de senha por e-mail

**Prioridade:** Média

##### 📝 Descrição

Backend completo para recuperação de senha. O frontend (`RecuperarSenhaForm`) já está pronto.

##### ✅ Critérios de Aceitação

- [ ] Token de uso único com TTL de 1 hora gerado e enviado por e-mail.
- [ ] Nova solicitação invalida token anterior.
- [ ] Link enviado em até 2 minutos.
- [ ] Token de uso único — segunda utilização retorna erro.

---

#### feat: bloqueio de conta após 5 tentativas falhas

**Prioridade:** Baixa

##### ✅ Critérios de Aceitação

- [ ] Conta bloqueada por 15 minutos após 5 tentativas consecutivas falhas.
- [ ] Contador de tentativas armazenado no Redis (TTL 15min).

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
| Logout com invalidação no servidor             | Alta                          |
| Worker batch Celery                            | Alta                          |
| Filtros afetando dashboard                     | Média                         |
| Cache Redis                                    | Média                         |
| Recuperação de senha                           | Média                         |
| Tempo por fase                                 | Média                         |
| Estimativa preditiva                           | Baixa (condicional ao volume) |
| Bloqueio de conta                              | Baixa                         |
