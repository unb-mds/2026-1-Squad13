# Arquitetura de Software

## Monitoramento de Tempo de Tramitação de Proposições

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

A lógica de "essa proposição está parada há mais de 180 dias" fica no banco (stored procedure), no backend (serviço Python) ou no frontend (JavaScript)?

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
│   Ex: BuscarProposicoesService                  │
├─────────────────────────────────────────────────┤
│                 Domínio                         │
│   Entidades · regras de negócio · cálculos      │
│   Zero dependências externas. Funciona sem      │
│   banco, sem HTTP, sem framework.               │
│   Ex: Proposicao · Tramitacao · dias_parada()   │
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

### Estratégia de Implementação Iterativa

O projeto adota a Layered Architecture como objetivo estrutural, evoluindo de mocks iniciais para integrações reais de forma progressiva.

**Estado Atual:**
O sistema já conta com a **integração real com banco de dados PostgreSQL** (ou SQLite para desenvolvimento local/testes) utilizando `SQLModel`. Esta escolha permitiu unificar as Entidades de Domínio com os Modelos de Persistência, reduzindo a complexidade de mapeamento nesta fase de MVP acadêmico.

**Próximos Passos:**
À medida que o desenvolvimento avança, o código será refinado para incluir:
1.  Implementação completa de `Adapters` reais para coleta automática das APIs da Câmara e Senado (atualmente em transição de mocks).
2.  Uso de `Redis` para cache de consultas frequentes.
3.  Configuração de `Celery` para orquestrar o processamento em lote (batch) de coleta de dados.

Essa abordagem evita o overhead de abstrações prematuras e permite que a equipe aprenda e aplique os conceitos arquiteturais passo a passo.

---

## Estratégia de Testes

**Decisão registrada em:** `docs/adr/ADR-007-testing-strategy.md`

O projeto adota uma pirâmide de testes focada em garantir a confiabilidade das regras de negócio e das integrações com APIs externas.

### Pirâmide de Testes

1.  **Testes de Unidade (`tests/unit/`):** Testam a lógica de negócio no Domínio e nos Serviços de Aplicação de forma isolada, sem dependências externas.
2.  **Testes de Integração (`tests/integration/`):** Testam a comunicação entre as camadas (Apresentação -> Aplicação -> Infraestrutura) e a integração com componentes como o banco de dados e APIs externas (usando mocks quando necessário).

---

## Estrutura de pastas

```text
/
├── ARCHITECTURE.md              ← este arquivo
├── README.md                    ← setup e como rodar
│
├── docs/
│   ├── adr/                     ← Architecture Decision Records
│   └── diagrams/                ← Diagramas C4 (PlantUML/Mermaid)
│
├── backend/
│   └── src/
│       ├── main.py
│       ├── presentation/        ← Camada de Apresentação (Controllers, Schemas)
│       │   └── controllers/
│       │       └── proposicao_controller.py
│       ├── application/         ← Camada de Aplicação (Services, Use Cases)
│       │   └── services/
│       │       ├── buscar_proposicoes_service.py
│       │       └── gerar_relatorio_service.py
│       ├── domain/              ← Camada de Domínio (Entidades, Regras de Negócio)
│       │   ├── entities/
│       │   │   ├── proposicao.py
│       │   │   └── tramitacao.py
│       │   └── exceptions.py
│       └── infrastructure/      ← Camada de Infraestrutura (DB, APIs, Cache)
│           ├── adapters/        ← Adaptores para APIs externas
│           ├── repositories/    ← Repositórios (SQLAlchemy, Mocks)
│           │   └── proposicao_repository.py
│           ├── cache/           ← Configuração de Cache (Redis)
│           └── workers/         ← Tarefas agendadas (Celery)
│
└── frontend/
    ├── src/
    │   ├── app/                 ← Configurações globais, rotas e providers
    │   ├── features/            ← Funcionalidades isoladas (ex: filtros, lista)
    │   ├── pages/               ← Páginas da aplicação
    │   ├── shared/              ← Componentes e libs compartilhados
    │   └── main.tsx
```

---

## Documentação de arquitetura

Utilizamos o **Modelo C4** para documentar a arquitetura em diferentes níveis de detalhe. Os diagramas estão em `docs/diagrams/`.

---

## ADRs — Architecture Decision Records

| ID      | Decisão                                           | Status   |
| ------- | ------------------------------------------------- | -------- |
| ADR-001 | Layered Architecture como padrão arquitetural     | Aceita   |
| ADR-002 | PostgreSQL como banco de dados                    | Aceita   |
| ADR-003 | FastAPI como framework do backend                 | Aceita   |
| ADR-004 | Batch diário como estratégia de coleta            | Aceita   |
| ADR-005 | Adapter pattern para isolamento das APIs externas | Aceita   |
| ADR-006 | Redis para cache de respostas                     | Aceita   |
| ADR-007 | Estratégia de Testes                              | Aceita   |

---

## Integração com as APIs Legislativas

O sistema normaliza os dados da Câmara e do Senado para a entidade de domínio `Proposicao`.

### Decisões de integração

1.  **Estratégia de coleta: batch diário** (ADR-004)
2.  **Normalização: adaptador por fonte** (ADR-005)
3.  **Deduplicação: por número canônico** (ex: `PL 1234/2023`)
4.  **Falhas: retry com backoff exponencial**

---

_Última atualização: consulte o histórico de commits do repositório._
