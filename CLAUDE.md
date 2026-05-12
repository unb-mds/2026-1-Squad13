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

- **Integrações externas:**
  - API da Câmara dos Deputados
  - API do Senado Federal

- **Persistência:**
  - PostgreSQL como fonte principal de dados
  - Redis para cache de consultas pesadas

- **Coleta de dados:**
  - Batch diário automatizado
  - Retry exponencial para falhas temporárias
  - Logs obrigatórios de execução

- **Testes:**
  - Pytest no backend — unitários e de integração (ver ADR-007)
  - Testes de frontend: Vitest com jsdom — smoke test e testes de utils compartilhadas
  - Testes unitários obrigatórios para domínio e services do backend

- **Containerização:**
  - Docker
  - Docker Compose para ambiente local

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

## CI/CD — Estado atual

GitHub Actions já está em uso com dois workflows separados por path filter:

- **`frontend.yml`** — dispara em PRs para `main` com mudanças em `frontend/**`
  - Passos: `npm ci` → `npm run lint` → `npm run test -- --run` → `npm run build`

- **`backend.yml`** — dispara em PRs para `main` com mudanças em `backend/**`
  - Passos: `uv sync` → `py_compile src/main.py`

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
- Adicionar comentários redundantes ou “comentários de cortesia”.
- Fazer otimizações prematuras sem evidência de necessidade.
- Alterar contratos de API sem alinhamento explícito.
- Mover responsabilidades entre camadas sem justificativa arquitetural.
- Colocar lógica de negócio no frontend.
- Acessar APIs externas fora da camada de adapters/infraestrutura.
- Criar componentes gigantes ou altamente acoplados.
- Ignorar tipagem TypeScript para “acelerar” implementação.
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

- Buscar proposições por:
  - número
  - autor
  - palavra-chave
  - tema

- Filtrar resultados por:
  - órgão de origem
  - tipo da proposição
  - status
  - período/data

- Exibir resultados em lista paginada.
- Permitir abertura da página detalhada da proposição.

### Critérios de aceitação

- A busca deve atualizar os resultados corretamente.
- Os filtros devem ser cumulativos.
- O botão “limpar filtros” deve resetar todos os filtros ativos.
- A lista deve suportar paginação.
- Cada item deve exibir:
  - tipo
  - número/ano
  - ementa resumida
  - status atual
  - órgão de origem
  - tempo de tramitação

## Plano

### Frontend

- Feature implementada como `proposicoes` (`frontend/src/features/proposicoes/`).
- Feature de filtros implementada como `filtros` (`frontend/src/features/filtros/`).
- Componentes principais já existem: `ProposicaoCard`, `PainelFiltros`.
- Criar camada de services para consumo da API real quando backend estiver pronto.

### Backend

- Criar endpoint:
  - `GET /proposicoes`
- Permitir query params:
  - texto
  - tipo
  - status
  - órgão
  - paginação
- Implementar paginação.
- Integrar adapters da Câmara e Senado.

## Tarefas

### Frontend

- [ ] Criar estrutura da feature `leis`
- [ ] Criar estrutura da feature `filtros`
- [ ] Implementar SearchBar
- [ ] Implementar painel de filtros
- [ ] Implementar listagem paginada
- [ ] Implementar navegação para detalhes
- [ ] Implementar estados de loading/erro/vazio

### Backend

- [ ] Criar endpoint de listagem
- [ ] Implementar paginação
- [ ] Criar service de busca
- [ ] Criar repository de consulta
- [ ] Integrar adapters externos

---

# Funcionalidade: Detalhamento da Proposição

## Spec

### Objetivo

Permitir que o usuário visualize informações completas sobre uma proposição legislativa e acompanhe sua tramitação.

### Requisitos funcionais

- Exibir:
  - título
  - ementa
  - autor
  - status atual
  - órgão atual
  - links oficiais

- Exibir linha do tempo da tramitação.
- Destacar atrasos superiores a 180 dias.
- Mostrar tempo total de tramitação.

### Critérios de aceitação

- Timeline deve estar ordenada da movimentação mais recente para a mais antiga.
- Etapas acima de 180 dias devem possuir destaque visual.
- Links externos devem abrir corretamente.
- Informações ausentes não devem quebrar a interface.

## Plano

### Frontend

- Criar página `detalhe-proposicao-page`.
- Criar componentes:
  - Timeline
  - PropositionDetailsCard
  - DelayBadge

### Backend

- Criar endpoint:
  - `GET /proposicoes/{id}`
- Consolidar dados da tramitação.
- Calcular tempo total e atrasos.

## Tarefas

### Frontend

- [ ] Criar página de detalhes
- [ ] Implementar timeline
- [ ] Implementar destaque de atraso
- [ ] Implementar links externos
- [ ] Implementar estado de carregamento

### Backend

- [ ] Criar endpoint de detalhes
- [ ] Implementar cálculo de tramitação
- [ ] Consolidar histórico
- [ ] Criar DTO de resposta

---

# Funcionalidade: Dashboard Analítico

## Spec

### Objetivo

Permitir análise visual de métricas legislativas e identificação de gargalos institucionais.

### Requisitos funcionais

- Exibir KPIs:
  - tempo médio
  - quantidade analisada
  - atrasos significativos
  - comissão mais lenta

- Exibir gráficos:
  - tempo por tipo
  - tempo por comissão
  - distribuição por status

### Critérios de aceitação

- Dashboard deve responder aos filtros aplicados.
- Dados devem ser exibidos corretamente mesmo com volume elevado.
- Gráficos devem possuir legendas claras.

## Plano

### Frontend

- Criar feature `dashboard`.
- Criar componentes:
  - KPI cards
  - gráficos
  - filtros globais

### Backend

- Criar endpoint:
  - `GET /dashboard/metricas`
- Agregar métricas previamente calculadas.
- Utilizar cache Redis.

## Tarefas

### Frontend

- [ ] Criar layout do dashboard
- [ ] Implementar cards KPI
- [ ] Implementar gráficos
- [ ] Implementar filtros globais

### Backend

- [ ] Criar endpoint de métricas
- [ ] Implementar agregações
- [ ] Configurar cache Redis

---

# Funcionalidade: Inteligência Preditiva

## Spec

### Objetivo

Exibir estimativas de tempo de aprovação baseadas em dados históricos.

### Requisitos funcionais

- Exibir previsão apenas quando houver dados suficientes.
- Exibir indicador de confiabilidade.
- Exibir disclaimer obrigatório.

### Critérios de aceitação

- Proposições sem dados suficientes não devem gerar previsão.
- O disclaimer deve estar sempre visível.
- A interface não deve apresentar previsão como garantia.

## Plano

### Frontend

- Criar componente PredictionCard.

### Backend

- Criar endpoint:
  - `GET /predicoes/{id}`
- Implementar modelo estatístico inicial.

## Tarefas

### Frontend

- [ ] Criar card de previsão
- [ ] Implementar estados de ausência de previsão

### Backend

- [ ] Criar endpoint preditivo
- [ ] Implementar cálculo estatístico
- [ ] Implementar score de confiança

---

# Funcionalidade: Autenticação

## Spec

### Objetivo

Permitir autenticação e gerenciamento de sessão de usuários.

### Requisitos funcionais

- Cadastro.
- Login.
- Logout.
- Recuperação de senha.

### Critérios de aceitação

- Login inválido deve exibir erro claro.
- Sessão deve expirar corretamente.
- Logout deve invalidar sessão.

## Plano

### Frontend

- Criar feature `auth`.
- Criar páginas:
  - login
  - cadastro
  - recuperação de senha

### Backend

- Criar endpoints:
  - `/auth/login`
  - `/auth/register`
  - `/auth/logout`
  - `/auth/recovery`
- Implementar JWT.

## Tarefas

### Frontend

- [ ] Criar formulários
- [ ] Implementar controle de sessão
- [ ] Implementar proteção de rotas

### Backend

- [ ] Criar endpoints de autenticação
- [ ] Implementar JWT
- [ ] Implementar expiração de sessão

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
5. Garantir consistência com:
   - Constituição
   - Convenções técnicas
   - Arquitetura
   - Funcionalidades
   - CI/CD

---

## Regra operacional obrigatória

Antes de iniciar qualquer nova implementação:

1. Releia completamente o `CLAUDE.md`.
2. Considere todas as decisões registradas anteriormente.
3. Utilize o contexto acumulado do projeto.
4. Nunca ignore arquitetura, convenções ou decisões persistentes previamente documentadas.