## Projeto

**Monitoramento de Tramitação de Leis** — plataforma web para análise da eficiência do processo legislativo brasileiro, permitindo consultar proposições, acompanhar tramitações, identificar gargalos institucionais e visualizar métricas analíticas e previsões de tempo de aprovação.

O sistema é focado em estudantes, pesquisadores, jornalistas, cidadãos e usuários interessados em transparência pública e análise legislativa baseada em dados.

---

## Constituição

### Confiabilidade e Qualidade

1. O sistema deve continuar funcional mesmo quando APIs externas da Câmara ou Senado estiverem indisponíveis temporariamente.
2. Toda coleta de dados legislativos deve ser rastreável, registrando falhas, sucessos e inconsistências em logs claros.
3. Nenhuma funcionalidade crítica deve depender exclusivamente de dados em tempo real; sempre prefira cache ou persistência local quando possível.
4. O sistema deve tratar dados incompletos sem quebrar a interface ou interromper fluxos do usuário.

### Arquitetura e Engenharia

5. Respeite rigorosamente a Layered Architecture: nenhuma camada pode acessar outra pulando níveis.
6. O domínio deve permanecer desacoplado de frameworks, banco de dados e APIs externas.
7. Toda integração externa deve ser isolada através de adapters para evitar acoplamento direto com provedores externos.
8. Prefira componentes reutilizáveis e desacoplados em vez de soluções rápidas e específicas.
9. Nenhuma regra de negócio complexa deve existir no frontend.

### Experiência do Usuário

10. O usuário deve entender rapidamente onde existem gargalos ou atrasos na tramitação legislativa através da interface.
11. Toda visualização analítica deve priorizar clareza e interpretação antes de estética.
12. O sistema deve sempre fornecer feedback visual para estados de carregamento, erro ou ausência de dados.
13. Filtros e buscas devem responder de forma previsível, imediata e consistente.

### Transparência e Ética

14. Toda previsão gerada por inteligência artificial deve deixar explícito que se trata apenas de uma estimativa estatística.
15. O sistema nunca deve apresentar inferências preditivas como garantias legais ou institucionais.

---

## Convenções técnicas

- **Frontend:**
  - React
  - TypeScript
  - Vite
  - Tailwind CSS 3
  - React Router
  - ESLint (flat config — `eslint.config.js`; executar: `npm run lint` a partir de `frontend/`)
  - Arquitetura baseada em Features
  - Componentização reutilizável

- **Backend:**
  - Python 3.12+
  - FastAPI
  - SQLModel (ORM sobre SQLAlchemy + Pydantic)
  - Ruff (linter)
  - Layered Architecture
  - Services + Domain + Adapters

- **Banco de dados:**
  - PostgreSQL

- **Cache:**
  - Redis

- **Workers assíncronos:**
  - Celery (worker + beat)
  - Task diária `coletar_proposicoes_diario` agendada às 02h37 (America/Sao_Paulo)

- **Integrações externas:**
  - API da Câmara dos Deputados
  - API do Senado Federal
  - Adapters mock disponíveis: `camara_mock_adapter.py`, `senado_mock_adapter.py`

- **Persistência:**
  - PostgreSQL como fonte principal de dados
  - Redis para cache de consultas pesadas

- **Coleta de dados:**
  - Batch diário automatizado via Celery Beat
  - Retry exponencial para falhas temporárias
  - Logs obrigatórios de execução via `LogColetaModel`

- **Testes:**
  - Pytest no backend — unitários e de integração (ver ADR-007)
  - Configuração do pytest centralizada em `backend/pyproject.toml`; nunca recriar `backend/pytest.ini`
  - Smoke test do endpoint raiz (`GET /`) já existe e deve ser mantido
  - Fixtures de backend devem refletir fielmente a entidade `Proposicao`
  - Testes de frontend: Vitest com jsdom + Testing Library — 31 testes em 7 arquivos (smoke, utils, Badge, EmptyState, Button, Spinner, ProposicaoCard); cleanup global em `setup.ts`; coverage local via `npm run test:coverage` (provider `@vitest/coverage-v8`, sem thresholds no CI)
  - Testes unitários obrigatórios para domínio e services do backend
  - CI do backend provisiona Redis como service (`redis:alpine` no GitHub Actions)

- **Containerização:**
  - Docker
  - Docker Compose para ambiente local (postgres, redis, pgadmin, backend, frontend, celery_worker, celery_beat)

- **Gerenciamento de dependências:**
  - npm no frontend
  - uv no backend (`pyproject.toml` + `uv.lock`; comandos: `uv sync`, `uv run`)

- **Concorrência e processamento:**
  - async/await no FastAPI
  - Processamento assíncrono para coleta e integrações externas

- **Estrutura arquitetural obrigatória:**
  - Layered Architecture no backend
  - Feature-Based Architecture no frontend
  - Adapter Pattern para integrações externas

- **Estrutura de pastas:**

```txt
backend/src/
├── presentation/
├── application/
├── domain/
└── infrastructure/

frontend/src/
├── app/
├── shared/
├── features/
├── pages/
└── main.tsx
```

---

## Arquitetura implementada — referência atual

### Backend — o que existe

**Application Services** (`backend/src/application/services/`):
- `auth_service.py` — autenticação JWT, login, cadastro, logout, lockout por tentativas
- `buscar_proposicoes_service.py` — busca com filtros e paginação
- `detalhe_proposicao_service.py` — detalhe de proposição
- `listar_movimentacoes_service.py` — movimentações com cache Redis; modos: COMPLETO, RESUMIDO, RELEVANTE
- `agregar_por_fase_service.py` — agrupa eventos em períodos por fase analítica
- `normalizar_tramitacao_service.py` — normalização de tramitações
- `dashboard_service.py` — métricas de dashboard com cache Redis
- `coletar_em_lote_service.py` — orquestra coleta batch da Câmara e do Senado
- `gerar_estimativa_service.py` — estimativa preditiva com threshold mínimo de amostra
- `recuperacao_senha_service.py` — fluxo de recuperação de senha

**Domain Entities** (`backend/src/domain/entities/`):
`Proposicao`, `EventoTramitacao`, `FaseAnalitica`, `FaseCodigo`, `OrgaoLegislativo`, `Tramitacao`, `Apensamento`, `User`

**Domain Value Objects** (`backend/src/domain/value_objects/`):
`ModoMovimentacao` (RESUMIDO | COMPLETO | RELEVANTE), `PeriodoFase`

**Domain Services** (`backend/src/domain/services/`):
`EstimativaAprovacaoService`, `LoginAttemptService`

**Infrastructure Adapters** (`backend/src/infrastructure/adapters/`):
`CamaraAdapter`, `SenadoAdapter`, `CamaraMockAdapter`, `SenadoMockAdapter`, `SecurityAdapter`, `RedisBlacklistAdapter`, `RedisLoginAttemptAdapter`, `DummyEmailSender`

**Infrastructure Repositories** (`backend/src/infrastructure/repositories/`):
`SQLProposicaoRepository`, `SQLEventoTramitacaoRepository`, `SQLFaseAnaliticaRepository`, `SQLOrgaoLegislativoRepository`, `SQLApensamentoRepository`, `SQLDashboardRepository`, `SQLUserRepository`

**Database Models** (`backend/src/infrastructure/database/models/`):
`ProposicaoModel`, `EventoTramitacaoModel`, `FaseAnaliticaModel`, `OrgaoLegislativoModel`, `ApensamentoModel`, `LogColetaModel`, `UserModel`

### Endpoints disponíveis

```
POST   /auth/register
POST   /auth/login
POST   /auth/logout
POST   /auth/recuperar-senha
POST   /auth/redefinir-senha
GET    /health
GET    /proposicoes
GET    /proposicoes/{id}
GET    /proposicoes/{id}/movimentacoes?modo=completo|resumido|relevante
GET    /proposicoes/estimativa/{tipo}/{tema}
GET    /dashboard/metricas
GET    /dashboard/grafico-tipo
GET    /dashboard/grafico-comissao
GET    /dashboard/grafico-status
GET    /dashboard/gargalos
GET    /dashboard/comparacao-temas
GET    /dashboard/tempo-por-fase
```

### Frontend — o que existe

**Pages** (`frontend/src/pages/`):
`dashboard-page`, `consulta-proposicoes-page`, `detalhe-proposicao-page`, `relatorios-page`, `login-page`, `cadastro-page`, `recuperar-senha-page`

**Features** (`frontend/src/features/`):
- `auth/` — LoginForm, CadastroForm, RecuperarSenhaForm
- `dashboard/` — DashboardComponents
- `filtros/` — PainelFiltros
- `relatorios/` — RelatorioComponents
- `tramitacoes/` — CardPrevisaoIA, TimelineTramitacao

**Shared** (`frontend/src/shared/`):
- `lib/api.ts` — cliente HTTP para todos os endpoints
- `lib/hooks/use-debounce.ts`
- `lib/mock-data.ts` — dados mock de fallback
- `lib/utils.ts`
- `shared/constants/index.ts` — constantes globais incluindo `DISCLAIMER_IA`
- `shared/types/index.ts` — tipos TypeScript para todas as entidades
- `shared/ui/index.tsx` — componentes compartilhados (Badge, Button, Spinner, EmptyState, ProposicaoCard)

**App** (`frontend/src/app/`):
- `providers/AuthProvider.tsx` + `AuthContext.tsx` — controle de sessão JWT
- `router/index.tsx` — roteamento com `PrivateRoute`
- `layouts/AppLayout.tsx`

---

## Convenções de nomenclatura

- Classes: `PascalCase`
- Componentes React: `PascalCase`
- Arquivos TypeScript/TSX: `kebab-case`
- Funções, variáveis e propriedades: `camelCase`
- Constantes globais: `UPPER_SNAKE_CASE`
- Rotas: `kebab-case`
- Testes: `descricaoDoComportamentoEsperado`

---

## Boas práticas obrigatórias

- Não colocar lógica de negócio complexa no frontend.
- Não acessar APIs externas fora da camada de infraestrutura.
- Não duplicar código reutilizável.
- Toda feature deve possuir responsabilidade única.
- Toda integração externa deve possuir adapter próprio.
- Controllers não devem conter regras de negócio.
- Domain não pode depender de framework, banco ou HTTP.
- Preferir composição em vez de acoplamento.
- Evitar componentes excessivamente grandes.
- Separar responsabilidades entre UI, estado e dados.

---

## UI/UX

- Interface responsiva obrigatória.
- Feedback visual obrigatório para:
  - loading
  - erro
  - vazio
- Componentes de loading devem incluir atributos ARIA adequados (`role="status"`, `aria-label`).
- Priorizar clareza analítica sobre efeitos visuais.
- Destaque visual para gargalos e atrasos significativos.
- Componentes devem manter consistência visual.
- Navegação deve ser simples e previsível.

---

## Dependências externas

- Bibliotecas externas devem ser minimizadas.
- Novas dependências devem possuir justificativa técnica clara.
- Evitar dependências abandonadas ou sem manutenção ativa.
- Preferir bibliotecas amplamente utilizadas e bem documentadas.

---

## Regras de Git e versionamento

- Nunca realizar alterações diretamente na branch `main`.
- Toda implementação deve ocorrer em branch separada.
- Sempre criar branch antes de iniciar qualquer tarefa.
- Padrões obrigatórios de branch:
  - `feat/<nome>`
  - `fix/<nome>`
  - `chore/<nome>`
  - `refactor/<nome>`
  - `docs/<nome>`
- Nunca versionar `node_modules/` — já configurado no `.gitignore`; jamais executar `git add` em `node_modules/`.
- Nunca fazer commit diretamente na `main`.
- Nunca fazer merge automaticamente na `main`.
- Pull Requests são obrigatórios para integração.
- Antes de iniciar qualquer implementação:
  1. verificar branch atual;
  2. confirmar que NÃO está na `main`;
  3. criar nova branch se necessário.
- Se o usuário solicitar alteração diretamente na `main`, avisar o risco antes de prosseguir.
- Fluxo padrão de features: `feature branch → develop → main`; mudanças de CI/base podem ir para `main` diretamente quando aplicável.
- Cada issue ou PR deve usar worktree e branch isolados.

### Fluxo operacional com Claude Code

- Claude Code não executa `git commit`, `git push` nem abre Pull Requests.
- Commits, push e abertura de PR são sempre feitos manualmente pelo usuário.
- Ao finalizar cada tarefa, Claude Code deve informar: path da worktree ativa, branch atual, resultado de `git status`, diff final e comandos exatos para execução manual.

## CI/CD — Estado atual

GitHub Actions já está em uso com workflows separados por path filter:

- **`frontend.yml`** — dispara em PRs para `main` e `develop` com mudanças em `frontend/**`
  - Passos: `npm ci` → `npm run lint` → `npm run test -- --run` → `npm run build`

- **`backend.yml`** — dispara em PRs para `main` e `develop` com mudanças em `backend/**`
  - Passos: `uv sync` → Ruff → `py_compile src/main.py` → pytest
  - Redis provisionado como service no CI (`redis:alpine`)

- **`cd-homologacao.yml`** — **deploy automático para VM GCP via SSH** a cada push na branch `develop` com mudanças em `backend/**`, `frontend/**`, `docker-compose.yml` ou `.env.example`
  - Executa `git pull origin develop && docker compose up -d --build` na VM remota

- **`deploy-squad-dashboard.yml`** e **`update-squad-dashboard-data.yml`** — deploy automático do painel interno para GitHub Pages

Regras:
- Não fazer merge sem CI verde.
- Não implementar CI/CD sem antes analisar a estrutura real do projeto.
- Não adicionar ferramentas novas ao pipeline sem solicitação explícita.
- Não fazer deploy automático sem solicitação explícita.
- Toda alteração de CI/CD ocorre em branch separada, nunca direto na `main`.
- Preferir uso do GitHub CLI (`gh`) para operações de Pull Request quando disponível no ambiente.

## Como me ajudar

- **Sempre proponha a mudança mínima** necessária para resolver a tarefa solicitada. Não refatore código não relacionado sem necessidade clara.
- **Se alguma mudança violar a Constituição do projeto, pare e avise antes de implementar.** Nunca ignore princípios arquiteturais silenciosamente.
- **Prefira implementar testes junto do código** sempre que existirem critérios objetivos de aceitação.
- **Implemente apenas uma responsabilidade por tarefa.** Evite misturar múltiplas features, correções ou refactors no mesmo diff.
- **Não invente decisões arquiteturais fora do escopo definido.** Caso exista ambiguidade sobre stack, estrutura ou abordagem, pergunte antes de assumir.
- **Respeite a arquitetura definida no projeto.**
  - Backend:
    - Layered Architecture
    - Adapter Pattern
  - Frontend:
    - Feature-Based Architecture
    - Component-Based UI
- **Nunca coloque lógica de negócio complexa no frontend.**
- **Toda integração externa deve passar pela camada de infraestrutura/adapters.**
- **Antes de qualquer implementação, leia os ADRs em `docs/adr/`.** Eles documentam decisões de stack, arquitetura e padrões que não devem ser repetidas ou revertidas sem alinhamento explícito.

- **Antes de commitar código no frontend, rode `npm run lint` a partir de `frontend/`.** O resultado deve ter 0 erros. Os 2 warnings conhecidos (`exhaustive-deps` e `react-refresh/only-export-components` em `AuthProvider.tsx`) são aceitos temporariamente.

- **Leia o contexto antes de modificar arquivos.** Entenda a feature, responsabilidade e impacto antes de editar.
- **Evite duplicação de código.** Prefira abstrações reutilizáveis quando fizer sentido.
- **Respeite a organização existente do projeto.** Antes de criar novos arquivos ou estruturas, verifique se já existe um local adequado.
- **Prefira componentes pequenos, reutilizáveis e desacoplados.**
- **Sempre mantenha tipagem explícita e clara em TypeScript.**
- **Toda interface deve tratar estados de loading, erro e vazio.**
- **Priorize clareza e legibilidade sobre otimizações prematuras.**
- **Mantenha consistência visual e arquitetural entre features.**
- **Commits devem ser pequenos, objetivos e seguir Conventional Commits.**
- **Não adicionar dependências externas sem necessidade real e justificativa técnica clara.**
- **Antes de implementar qualquer funcionalidade, analise o contexto e faça perguntas quando houver ambiguidade.**
  Nunca assuma regras de negócio, arquitetura, comportamento esperado ou decisões técnicas sem confirmação explícita.

- **Se existir mais de uma abordagem válida, apresente opções antes de implementar.**
  Explique vantagens, desvantagens e impacto arquitetural de cada opção.

- **Quando faltar contexto suficiente para uma implementação segura, pare e pergunte antes de continuar.**

- **Sempre valide entendimento da tarefa antes de modificar múltiplos arquivos ou estruturas importantes.**

- **Prefira esclarecer dúvidas cedo em vez de corrigir decisões erradas depois.**
- **Nunca invente endpoints, contratos de API, estruturas de banco ou respostas sem confirmação ou evidência no projeto.**

---

## Fora de escopo padrão

A menos que explicitamente solicitado, **não faça**:

- Adicionar novas dependências externas.
- Alterar arquitetura definida no projeto.
- Reformatar arquivos inteiros sem necessidade.
- Alterar convenções de nomenclatura existentes.
- Modificar estrutura de pastas já definida.
- Refatorar código não relacionado à tarefa atual.
- Alterar testes de outras funcionalidades.
- Criar mocks desnecessários fora do escopo solicitado.
- Implementar funcionalidades além da tarefa pedida.
- Criar documentação extra não solicitada.
- Adicionar comentários redundantes ou "comentários de cortesia".
- Fazer otimizações prematuras sem evidência de necessidade.
- Alterar contratos de API sem alinhamento explícito.
- Mover responsabilidades entre camadas sem justificativa arquitetural.
- Colocar lógica de negócio no frontend.
- Acessar APIs externas fora da camada de adapters/infraestrutura.
- Criar componentes gigantes ou altamente acoplados.
- Ignorar tipagem TypeScript para "acelerar" implementação.
- Alterar padrões visuais globais sem solicitação explícita.
- Fazer commits automaticamente sem revisão explícita.
- Gerar código que viole a Constituição do projeto.

---

## Funcionalidades

---

# Funcionalidade: Consulta de Proposições

## Spec

### Objetivo

Permitir que usuários consultem proposições legislativas de forma rápida e eficiente através de busca textual e filtros avançados.

### Requisitos funcionais

- Buscar proposições por: número, autor, palavra-chave, tema
- Filtrar resultados por: órgão de origem, tipo, status, período/data
- Exibir resultados em lista paginada
- Permitir abertura da página detalhada da proposição

### Critérios de aceitação

- A busca deve atualizar os resultados corretamente.
- Os filtros devem ser cumulativos.
- O botão "limpar filtros" deve resetar todos os filtros ativos.
- A lista deve suportar paginação.
- Cada item deve exibir: tipo, número/ano, ementa resumida, status atual, órgão de origem, tempo de tramitação.

## Tarefas

### Frontend
- [x] Criar estrutura da feature `filtros`
- [x] Implementar SearchBar e painel de filtros (`PainelFiltros`)
- [x] Implementar listagem paginada (`consulta-proposicoes-page`)
- [x] Implementar navegação para detalhes
- [x] Implementar estados de loading/erro/vazio
- [x] Integrar `listarProposicoes` com API real

### Backend
- [x] Criar endpoint `GET /proposicoes` com query params
- [x] Implementar paginação
- [x] Criar `BuscarProposicoesService`
- [x] Criar `SQLProposicaoRepository` com filtros
- [x] Integrar adapters Câmara e Senado

---

# Funcionalidade: Detalhamento da Proposição

## Spec

### Objetivo

Permitir que o usuário visualize informações completas sobre uma proposição legislativa e acompanhe sua tramitação.

### Requisitos funcionais

- Exibir: título, ementa, autor, status atual, órgão atual, links oficiais
- Exibir linha do tempo da tramitação
- Destacar atrasos superiores a 180 dias
- Mostrar tempo total de tramitação

### Critérios de aceitação

- Timeline deve estar ordenada da movimentação mais recente para a mais antiga.
- Etapas acima de 180 dias devem possuir destaque visual.
- Links externos devem abrir corretamente.
- Informações ausentes não devem quebrar a interface.

## Tarefas

### Frontend
- [x] Criar página `detalhe-proposicao-page`
- [x] Implementar `TimelineTramitacao`
- [x] Implementar destaque de atraso (`temAtraso`)
- [x] Implementar links externos
- [x] Implementar estado de carregamento

### Backend
- [x] Criar endpoint `GET /proposicoes/{id}`
- [x] Criar endpoint `GET /proposicoes/{id}/movimentacoes?modo=completo|resumido|relevante`
- [x] Implementar cálculo de tempo e atraso (`diasNaEtapa`, `temAtraso`)
- [x] Consolidar histórico via `ListarMovimentacoesService` com cache Redis
- [x] Criar `AgregarPorFaseService` para agrupamento por fase
- [ ] **Pendente (#169):** Interface visual de status de atraso e explicabilidade

---

# Funcionalidade: Dashboard Analítico

## Spec

### Objetivo

Permitir análise visual de métricas legislativas e identificação de gargalos institucionais.

### Requisitos funcionais

- Exibir KPIs: tempo médio, quantidade analisada, atrasos significativos, comissão mais lenta
- Exibir gráficos: tempo por tipo, tempo por comissão, distribuição por status
- Dashboard deve responder a filtros aplicados

### Critérios de aceitação

- Dashboard deve responder aos filtros aplicados.
- Dados devem ser exibidos corretamente mesmo com volume elevado.
- Gráficos devem possuir legendas claras.

## Tarefas

### Frontend
- [x] Criar layout do dashboard (`dashboard-page`)
- [x] Implementar cards KPI
- [x] Implementar gráficos
- [x] Implementar `PainelFiltros` para filtros globais
- [ ] **Pendente (#91):** Filtros ativos refletindo nos dados do dashboard
- [ ] **Pendente (#89):** Tempo por fase com dados reais integrados

### Backend
- [x] Criar endpoints de métricas (`GET /dashboard/*`)
- [x] Implementar `DashboardService` com agregações e cache Redis
- [x] Configurar cache Redis
- [x] Criar `SQLDashboardRepository`
- [ ] **Pendente (#165–#168):** Infraestrutura, serviço e endpoints de métricas de atraso (IAR, IAF, IEI)

---

# Funcionalidade: Inteligência Preditiva

## Spec

### Objetivo

Exibir estimativas de tempo de aprovação baseadas em dados históricos.

### Requisitos funcionais

- Exibir previsão apenas quando houver dados suficientes (threshold: 50 registros históricos)
- Exibir indicador de confiabilidade
- Exibir disclaimer obrigatório

### Critérios de aceitação

- Proposições sem dados suficientes não devem gerar previsão.
- O disclaimer deve estar sempre visível.
- A interface não deve apresentar previsão como garantia.

## Tarefas

### Frontend
- [x] Criar `CardPrevisaoIA` com disclaimer obrigatório (`DISCLAIMER_IA`)
- [x] Implementar estado de ausência de previsão

### Backend
- [x] Criar endpoint `GET /proposicoes/estimativa/{tipo}/{tema}`
- [x] Implementar `GerarEstimativaUseCase` + `EstimativaAprovacaoService`
- [x] Implementar score de confiança e threshold mínimo
- [ ] **Pendente (#145):** Cobertura de testes para `GerarEstimativaUseCase`

---

# Funcionalidade: Autenticação

## Spec

### Objetivo

Permitir autenticação e gerenciamento de sessão de usuários.

### Requisitos funcionais

- Cadastro, Login, Logout, Recuperação de senha

### Critérios de aceitação

- Login inválido deve exibir erro claro.
- Sessão deve expirar corretamente.
- Logout deve invalidar sessão (token blacklist via Redis).
- Lockout por excesso de tentativas deve ser aplicado.

## Tarefas

### Frontend
- [x] Criar formulários de login, cadastro e recuperação de senha
- [x] Implementar `AuthProvider` + `AuthContext` com controle de sessão JWT
- [x] Implementar proteção de rotas via `PrivateRoute`
- [ ] **Pendente:** Integrar `recuperarSenhaApi` com endpoint real (atualmente usa `delay(1200)`)

### Backend
- [x] Criar endpoints `/auth/login`, `/auth/register`, `/auth/logout`, `/auth/recuperar-senha`, `/auth/redefinir-senha`
- [x] Implementar JWT com `jose`
- [x] Implementar blacklist de tokens via Redis
- [x] Implementar lockout por tentativas (`LoginAttemptService` + `RedisLoginAttemptAdapter`)
- [x] Implementar `RecuperacaoSenhaService`

---

# Funcionalidade: Coleta Batch

## Spec

### Objetivo

Coletar proposições diariamente da Câmara e do Senado de forma automatizada, idempotente e rastreável.

## Tarefas

- [x] Criar `ColetarEmLoteService` com orquestração Câmara + Senado
- [x] Criar `CamaraAdapter` e `SenadoAdapter` com retry
- [x] Criar `CamaraMockAdapter` e `SenadoMockAdapter` para testes
- [x] Configurar Celery App com broker/backend Redis
- [x] Criar `task_coletar_proposicoes_diario` (Celery Beat, 02h37 diário)
- [x] Registrar execuções em `LogColetaModel`
- [ ] **Pendente (#87):** Fechar issue — worker está implementado mas issue permanece aberta
- [ ] **Pendente (#167):** Worker de atualização de métricas de atraso

---

# Memória evolutiva do projeto

## Objetivo

Este arquivo deve evoluir junto com o projeto.

Sempre que uma funcionalidade, arquitetura, workflow, integração, convenção ou decisão relevante for implementada e aprovada via Pull Request, o contexto correspondente deve ser incorporado neste `CLAUDE.md`.

O objetivo é garantir que:
- a IA sempre possua contexto atualizado;
- decisões anteriores não sejam esquecidas;
- padrões arquiteturais sejam mantidos;
- novas implementações respeitem histórico técnico do projeto.

---

## Regras obrigatórias de atualização

- Após merge de um PR aprovado, analisar:
  - funcionalidades adicionadas;
  - decisões arquiteturais;
  - novas convenções;
  - novos workflows;
  - mudanças estruturais;
  - integrações;
  - padrões recorrentes.

- Se a mudança alterar o comportamento esperado do projeto, atualizar este arquivo.

- Nunca duplicar informações já existentes.
- Sempre preferir evolução incremental da documentação existente.
- Não transformar este arquivo em changelog técnico detalhado.
- Registrar apenas contexto persistente e relevante para futuras implementações.

---

## O que DEVE ser atualizado aqui

### Arquitetura
- novos padrões arquiteturais;
- mudanças de estrutura;
- novas camadas;
- novas responsabilidades.

### Convenções técnicas
- novas bibliotecas aprovadas;
- novos padrões obrigatórios;
- mudanças de stack;
- novos padrões de testes.

### CI/CD
- novos workflows;
- novas validações obrigatórias;
- proteção de branch;
- pipelines;
- estratégias de deploy.

### Funcionalidades
- funcionalidades persistentes do sistema;
- comportamento esperado;
- integrações relevantes;
- regras de negócio importantes.

### Boas práticas
- padrões que se tornaram recorrentes;
- decisões tomadas em múltiplos PRs;
- restrições técnicas relevantes.

---

## O que NÃO deve ser registrado

- detalhes temporários;
- bugs pontuais;
- experimentos descartados;
- logs;
- mudanças irrelevantes;
- descrições completas de PRs;
- histórico detalhado de commits.

---

## Fluxo obrigatório após cada PR aprovado

1. Ler as mudanças aprovadas no PR.
2. Identificar impactos persistentes no projeto.
3. Atualizar o `CLAUDE.md` se necessário.
4. Manter o arquivo organizado e sem duplicação.
5. Garantir consistência com: Constituição, Convenções técnicas, Arquitetura, Funcionalidades, CI/CD.

---

## Regra operacional obrigatória

Antes de iniciar qualquer nova implementação:

1. Releia completamente o `CLAUDE.md`.
2. Considere todas as decisões registradas anteriormente.
3. Utilize o contexto acumulado do projeto.
4. Nunca ignore arquitetura, convenções ou decisões persistentes previamente documentadas.
