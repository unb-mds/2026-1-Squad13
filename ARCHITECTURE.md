# Arquitetura de Software
## Monitoramento de Tempo de Tramitação de Leis

---

## O que é arquitetura de software

Arquitetura de software é o conjunto de **decisões estruturais importantes** sobre um sistema — decisões que são difíceis de mudar depois, que afetam múltiplas partes do código, e que determinam como o sistema vai se comportar ao longo do tempo.

Uma forma simples de pensar: se você pode mudar algo em 10 minutos sem consultar ninguém, isso é implementação. Se mudar exige realinhar o time, reescrever módulos ou redesenhar integrações — isso é arquitetura.

---

## Decisões arquiteturais

### Como o sistema é dividido em partes

Existe um frontend separado do backend? Existe um processo separado só para coletar dados das APIs da Câmara e do Senado, ou isso fica misturado com o restante da lógica?

### Como essas partes se comunicam

O frontend chama o backend via REST? GraphQL? O worker de coleta escreve direto no banco ou passa por uma fila?

### Onde ficam as regras de negócio

A lógica de "essa lei está parada há mais de 180 dias" fica no banco (stored procedure), no backend (serviço Python) ou no frontend (JavaScript)?

### Como o sistema lida com falhas externas

O que acontece quando a API do Senado está fora do ar? O sistema trava, retorna dados velhos do cache, ou exibe um aviso?

---

## Aplicação ao projeto

**Trabalho paralelo com 6 pessoas.** Sem estrutura definida, o dev pode criar lógica de negócio no controller, o designer criar endpoints no frontend e termos conflitos de merge e decisões inconsistentes. A arquitetura é o contrato que permite trabalho paralelo.

**Dependência de APIs externas.** A Câmara pode mudar o formato de resposta, o Senado pode adicionar autenticação. Se o código que chama essas APIs estiver espalhado por todo o sistema, qualquer mudança vira um pesadelo. Se estiver isolado em uma camada, é uma alteração cirúrgica.

---

## Padrão arquitetural adotado: Layered Architecture

**Decisão registrada em:** `docs/adr/ADR-001-layered-architecture.md`

O sistema é dividido em 4 camadas horizontais. Cada camada só conversa com a camada imediatamente abaixo. Nenhuma camada "pula" outra, e as camadas de baixo não conhecem as de cima.

```
┌─────────────────────────────────────────────────┐
│               Apresentação                      │
│   FastAPI · controllers · schemas de resposta   │
│   Recebe requisições HTTP. Não tem regra de     │
│   negócio. Não acessa banco nem APIs externas.  │
├─────────────────────────────────────────────────┤
│                Aplicação                        │
│   Services · casos de uso · orquestração        │
│   Sabe O QUE fazer. Delega o COMO para baixo.   │
│   Ex: BuscarLeisParadasService                  │
├─────────────────────────────────────────────────┤
│                 Domínio                         │
│   Entidades · regras de negócio · cálculos      │
│   Zero dependências externas. Funciona sem      │
│   banco, sem HTTP, sem framework.               │
│   Ex: Lei · Tramitacao · dias_parada()          │
├─────────────────────────────────────────────────┤
│              Infraestrutura                     │
│   Banco · APIs externas · Cache · Workers       │
│   Único lugar que conhece detalhes técnicos.    │
│   Ex: CamaraAdapter · SenadoAdapter · Redis     │
└─────────────────────────────────────────────────┘

Regra: dependências sempre apontam para baixo.
O Domínio não importa nada das outras camadas.
```

### Por que não MVC

MVC foi pensado para aplicações web monolíticas com interface acoplada. O Controller acumula chamadas às APIs externas, cache, regras de negócio e persistência — o chamado "Fat Controller". Difícil de testar e de manter quando as APIs externas mudam.

### Por que não Clean Architecture agora

Clean Architecture é a evolução natural da Layered e seria a escolha ideal para um sistema de longa vida. Para um projeto semestral com time em formação, o overhead de abstrações (ports, adapters, interfaces) atrasa entregas. O código será estruturado de forma a facilitar a migração futura.

---

## Estrutura de pastas

```
/
├── ARCHITECTURE.md              ← este arquivo
├── README.md                    ← setup e como rodar
│
├── docs/
│   ├── adr/
│   │   ├── README.md            ← índice de todas as ADRs
│   │   ├── ADR-001-layered-architecture.md
│   │   ├── ADR-002-postgresql.md
│   │   ├── ADR-003-fastapi.md
│   │   ├── ADR-004-batch-coleta.md
│   │   └── ADR-005-adapter-pattern.md
│   │
│   └── diagrams/
│       ├── c4-context.md        ← Nível 1: contexto do sistema
│       ├── c4-container.md      ← Nível 2: containers e tecnologias
│       └── c4-component-backend.md  ← Nível 3: módulos do backend
│
└── src/
    ├── domain/
    │   ├── entities/
    │   │   ├── lei.py
    │   │   └── tramitacao.py
    │   └── exceptions.py
    ├── application/
    │   └── services/
    │       ├── buscar_leis_paradas_service.py
    │       └── gerar_relatorio_service.py
    ├── infrastructure/
    │   ├── adapters/
    │   │   ├── camara_adapter.py
    │   │   └── senado_adapter.py
    │   ├── repositories/
    │   │   └── lei_repository.py
    │   └── cache/
    │       └── redis_cache.py
    └── presentation/
        └── controllers/
            └── lei_controller.py
```

---

## Documentação de arquitetura

Arquitetura de software é invisível — ela existe nas decisões, não no código. Documentar arquitetura é tornar essas decisões visíveis para pessoas diferentes, com níveis de detalhe diferentes.

### Modelo adotado: C4

**Decisão:** C4 Model (Simon Brown, 2018)

O C4 funciona como um mapa com escalas diferentes: do geral para o detalhe, cada nível serve um público diferente.

| Nível | Nome | Público | O que mostra |
|-------|------|---------|--------------|
| 1 | Context | Todos (prof., PO, time) | O sistema no mundo: usuários e sistemas externos |
| 2 | Container | Devs, PO | Processos internos: frontend, backend, worker, banco |
| 3 | Component | Devs | Módulos internos de cada container |
| 4 | Code | Opcional | Classes e interfaces (UML de classes) |

**Por que não UML puro:** genérico demais, ferramentas pesadas, difícil de versionar no Git.  
**Por que não arc42:** 12 seções, metade seria "não aplicável" no escopo acadêmico.  
**Por que não 4+1 Views:** pensado para times grandes com perspectivas radicalmente distintas.

Os diagramas C4 do projeto estão em `docs/diagrams/`.

---

## ADRs — Architecture Decision Records

Um ADR é um documento curto que responde: "por que tomamos essa decisão, e o que consideramos antes". Cada decisão relevante gera um arquivo na pasta `docs/adr/`.

### Template de ADR

```markdown
# ADR-00X: [Título curto da decisão]

**Data:** YYYY-MM-DD
**Status:** Proposta | Aceita | Depreciada | Substituída por ADR-XXX
**Decisores:** [nomes ou papéis]

## Contexto
[O problema ou força que exige uma decisão.]

## Decisão
[A escolha feita, em voz ativa. "Vamos usar X porque Y."]

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| ...   | ...  | ...     |

## Consequências

**Positivas:** ...  
**Negativas / trade-offs:** ...  
**Riscos:** ...
```

### ADRs registradas

| ID | Decisão | Status |
|----|---------|--------|
| ADR-001 | Layered Architecture como padrão arquitetural | Proposta |
| ADR-002 | PostgreSQL como banco de dados | Proposta |
| ADR-003 | FastAPI como framework do backend | Proposta |
| ADR-004 | Batch diário como estratégia de coleta | Proposta |
| ADR-005 | Adapter pattern para isolamento das APIs externas | Proposta |
| ADR-006 | Redis para cache de respostas | Proposta |

> **Regra:** toda mudança de decisão gera uma ADR nova que supersede a anterior.
> Não se edita uma ADR aceita — cria-se ADR-00X com status "Substituída por ADR-00Y".

---

## Stack tecnológica

**Exemplo(Ainda não decidido)**:

| Camada | Tecnologia | Justificativa |
|--------|-----------|---------------|
| Backend | FastAPI (Python) | I/O assíncrono reduz tempo de espera nas chamadas às APIs externas |
| Frontend | React + Vite | Vite resolve build lento; ecossistema conhecido pelo time |
| Banco de dados | PostgreSQL | Funções de janela para agregações temporais (tempo médio por tema, ano, relator) |
| Cache | Redis | APIs legislativas têm rate limiting implícito; dados mudam no máximo uma vez ao dia |
| Worker | Celery + Celery Beat | Coleta periódica agendada sem bloquear a API principal |
| Container | Docker Compose | Sobe PostgreSQL + Redis + Backend juntos em desenvolvimento |
| CI/CD | GitHub Actions | Pipeline de testes e deploy integrado ao repositório |

---

## Integração com as APIs Legislativas

> ⚠ Esta é a parte de maior risco técnico do sistema.
> Leia esta seção antes de qualquer implementação de coleta.

A API da Câmara (`dadosabertos.camara.leg.br`) e a do Senado (`legis.senado.leg.br`) têm formatos diferentes — o que reforça a necessidade da camada de Infraestrutura isolar essas diferenças do resto do sistema.

### Fontes de dados

| Fonte | Base URL | Formato | Autenticação |
|-------|----------|---------|--------------|
| Câmara | dadosabertos.camara.leg.br/api/v2 | JSON | Nenhuma |
| Senado | legis.senado.leg.br/sicon/rest | JSON | Nenhuma |

### Endpoints utilizados

**Câmara:**
```
GET /proposicoes                        → lista proposições (paginado)
GET /proposicoes/{id}                   → detalhe da proposição
GET /proposicoes/{id}/tramitacoes       → histórico de tramitação
GET /proposicoes/{id}/autores           → autores
```

**Senado:**
```
GET /materia/pesquisa                   → busca matérias
GET /materia/{codigo}                   → detalhe da matéria
GET /materia/{codigo}/movimentacoes     → histórico de tramitação
GET /materia/{codigo}/relatorias        → relatorias
```

### Diferença crítica

A Câmara usa o termo "proposição"; o Senado usa "matéria". São a mesma entidade com nomes e campos diferentes. O sistema normaliza os dois formatos para a entidade de domínio `Lei`.

### Decisões de integração

**1. Estratégia de coleta: batch diário**  
Worker executa todo dia às 02h (horário de Brasília). O usuário sempre lê do banco local, nunca da API diretamente. Isso garante funcionamento mesmo quando as APIs estão instáveis.  
→ `docs/adr/ADR-004-batch-coleta.md`

**2. Normalização: adaptador por fonte**  
`CamaraAdapter` e `SenadoAdapter` convertem cada formato para a entidade `Lei` do domínio. O restante do sistema não sabe que existem duas fontes.  
→ `docs/adr/ADR-005-adapter-pattern.md`

**3. Deduplicação: por número canônico**  
Formato: `{sigla} {numero}/{ano}` — ex: `PL 1234/2023`. Uma lei que tramita nas duas casas tem um único registro no banco. Estratégia: upsert por número canônico.

**4. Falhas: retry com backoff exponencial**  
3 tentativas: 1s → 2s → 4s. Se todas falharem: log de erro + alerta. Coleta parcial (uma fonte falha, a outra não) é aceitável — o sistema registra quais fontes foram coletadas em cada execução.

**5. Cache: TTL de 1 hora para leituras**  
Respostas das APIs armazenadas no Redis. Worker invalida o cache após cada coleta bem-sucedida.

**6. Paginação — atenção**  
A Câmara retorna no máximo 100 itens por página. É necessário iterar todas as páginas na coleta. Parâmetros: `?itens=100&pagina=1` (incrementar `pagina` até `dados` retornar vazio).

---

## O que o time precisa estudar

Esta seção mapeia cada decisão técnica ao conhecimento necessário. Serve como checklist de onboarding e referência durante o desenvolvimento.

### Toda a equipe

- [ ] **Layered Architecture** — como as camadas se comunicam e o que não pode cruzar fronteiras  
  Recurso: `ARCHITECTURE.md` (este arquivo) + `ADR-001`

- [ ] **Modelo C4** — como ler os diagramas do projeto  
  Recurso: [c4model.com](https://c4model.com) (introdução em 10 min)

- [ ] **ADRs** — como ler e propor novas decisões  
  Recurso: `docs/adr/README.md`

### Devs (implementação backend)

- [ ] **FastAPI** — roteamento, Pydantic, async/await  
  Recurso: [fastapi.tiangolo.com/tutorial](https://fastapi.tiangolo.com/tutorial)  
  Por quê: framework da camada de Apresentação

- [ ] **HTTPX** — cliente HTTP assíncrono  
  Recurso: [python-httpx.org](https://www.python-httpx.org)  
  Por quê: usado nos adapters para chamar as APIs externas

- [ ] **Paginação da API da Câmara**  
  Recurso: [dadosabertos.camara.leg.br/swagger-ui](https://dadosabertos.camara.leg.br/swagger-ui)  
  Por quê: coleta completa exige iterar todas as páginas

- [ ] **Celery + Celery Beat** — tarefas agendadas  
  Recurso: [docs.celeryq.dev — periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html)  
  Por quê: executa o worker de coleta diária

- [ ] **SQLAlchemy async** — ORM assíncrono  
  Recurso: [docs.sqlalchemy.org — asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)  
  Por quê: acesso ao PostgreSQL na camada de Infraestrutura

- [ ] **Tenacity** — retry com backoff exponencial  
  Recurso: [tenacity.readthedocs.io](https://tenacity.readthedocs.io)  
  Por quê: resiliência nas chamadas às APIs externas

### Arquiteto / DevOps

- [ ] **Padrão Adapter** — como isolar sistemas externos  
  Recurso: [refactoring.guru/design-patterns/adapter](https://refactoring.guru/design-patterns/adapter)  
  Por quê: `CamaraAdapter` e `SenadoAdapter` seguem este padrão

- [ ] **Redis** — estruturas de dados, TTL, invalidação de cache  
  Recurso: [redis.io/docs/data-types](https://redis.io/docs/data-types)  
  Por quê: camada de cache entre APIs externas e banco

- [ ] **Docker Compose** — orquestração local de serviços  
  Recurso: [docs.docker.com/compose](https://docs.docker.com/compose)  
  Por quê: sobe PostgreSQL + Redis + Backend juntos

- [ ] **GitHub Actions** — pipelines de CI/CD  
  Recurso: [docs.github.com/en/actions](https://docs.github.com/en/actions)  
  Por quê: pipeline de testes automáticos e deploy

- [ ] **12-Factor App — config**  
  Recurso: [12factor.net/config](https://12factor.net/config)  
  Por quê: URLs das APIs e credenciais do banco sem hardcode no código

### Designer (integração com backend)

- [ ] **OpenAPI / Swagger** — como ler a documentação da API gerada pelo FastAPI  
  Recurso: [swagger.io/docs/specification/about](https://swagger.io/docs/specification/about/)  
  Por quê: o backend expõe Swagger automaticamente; designer lê para integrar o frontend sem esperar o dev

---

*Última atualização: consulte o histórico de commits do repositório.*