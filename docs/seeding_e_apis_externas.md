# Arquitetura de Seeds Inteligentes e Integrações de APIs Externas no LexTrack

Este documento detalha o mapeamento de ponta a ponta da arquitetura de ingestão adaptativa, tratamento de resiliência e a orquestração do preenchimento de lacunas (seeds históricos) no projeto LexTrack.

---

## 1. Contexto e Objetivos

O LexTrack monitora o tempo de tramitação de leis (PLs e PECs) no Congresso Nacional. Para realizar análises históricas robustas e calcular baselines de confiabilidade, o banco de dados do LexTrack precisa manter uma cobertura de dados idêntica à das fontes oficiais (Câmara dos Deputados e Senado Federal).

### O Desafio
*   **APIs Instáveis e Limitadas**: As APIs do governo sofrem com quedas frequentes, tempos de resposta voláteis (Cold Starts/picos de uso) e políticas agressivas de limite de requisições (`HTTP 429 Too Many Requests`).
*   **Incerteza de Cobertura**: Simplesmente executar uma carga estática de sementes (seeds) não garante que registros deletados, alterados ou criados tardiamente sejam capturados.
*   **Necessidade de Execução 24/7 Autônoma**: O sistema precisa rodar continuamente no Celery sem causar bloqueio de IPs, reagindo dinamicamente à saúde das APIs externas.

---

## 2. Visão Geral da Arquitetura do Motor de Ingestão

A arquitetura respeita estritamente o padrão de **Layered Architecture** e o isolamento de domínio definidos nas regras do projeto:

```
┌────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION                              │
│                      (FastAPI Endpoints / Controllers)                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION                               │
│  Ports: CacheProviderPort, CamaraAdapterPort, SenadoAdapterPort        │
│  Services: PreencherLacunasService, DetalheProposicaoService           │
│  Orchestration: Celery Workers (coleta_worker)                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                                 DOMAIN                                 │
│  Entities: Proposicao, Evento                                          │
│  Exceptions: ApiConnectionError, ApiRateLimitError, ApiServerError...  │
│  Business Rules: Classificação Preditiva (Poder Executivo, Economia)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                             INFRASTRUCTURE                             │
│  Adapters: CamaraAdapter, SenadoAdapter, RedisClient (CacheProvider)   │
│  Persistence: SQLProposicaoRepository (PostgreSQL via SQLModel)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Fluxo de Execução de Ponta a Ponta

O preenchimento de lacunas ocorre de forma cíclica e autônoma, mapeado nos seguintes passos:

### Fase 1: Detecção de Lacunas
1.  **Iteração Histórica**: O serviço varre os anos do presente (ano atual) até 1988 (ano da Constituição Federal) para os tipos `PL` e `PEC`.
2.  **Verificação de Pruning**: Se o ano/tipo/fonte estiver marcado no Redis como consolidado permanentemente (TTL infinito) ou sincronizado temporariamente (TTL 12h para o ano corrente), ele é ignorado sem consultas ao banco ou à API.
3.  **Comparação Local vs Externo**:
    *   Consulta o banco de dados local para obter a contagem de proposições salvas: `SQLProposicaoRepository.contar(...)`.
    *   Consulta a API externa (com cache Redis de 24 horas) para obter a totalização oficial: `Adapter.obter_total(...)`.
    *   Se a cobertura local for inferior a $95.0\%$, a lacuna é classificada como ativa e adicionada à fila de prioridades.
    *   Se a cobertura for $\ge 99.5\%$ em um ano histórico, o ano é marcado como consolidado permanentemente e retirado de futuras buscas.

### Fase 2: Entrada e Proteção de Overlap
1.  O Celery Beat aciona a tarefa `task_preencher_lacunas` a cada **15 minutos**.
2.  **Lock Global**: O worker tenta adquirir o lock exclusivo de execução no Redis (`seeding:lock:task_executando`). Se outra tarefa já estiver rodando, esta rodada aborta de imediato para evitar concorrência e race conditions.

### Fase 3: Processamento e Reserva de Offset
1.  O serviço extrai a lacuna pendente de maior prioridade (anos mais recentes primeiro).
2.  **Reserva de Offset**: O worker consulta o cursor de paginação atual do Redis (`seeding:cursor:{fonte}:{ano}:{tipo}`) e tenta reservar o bloco de processamento gravando uma chave de lock temporária baseada em token único (`seeding:lock:processando:...:{offset}`).
    *   Isso impede que múltiplos workers em paralelo baixem a mesma página de proposições da API externa.
3.  **Listagem de IDs**: O adaptador da fonte lista os IDs da página correspondente.
    *   **Tratamento de Lote Vazio (Fim do Histórico)**: Se a listagem retornar vazia em um ano histórico, o ano é consolidado e o cursor é deletado. Se for o ano atual, o cursor é resetado para `0` e o cooldown de 12 horas é ativado.

### Fase 4: Download Concorrente Resiliente
1.  Instancia-se um semáforo assíncrono (`asyncio.Semaphore`) com o limite dinâmico atualizado pelo Redis.
2.  Disparam-se as requisições em paralelo para cada ID coletado no lote, passando pelo **Rate Limiter temporal** individual (`AsyncRateLimiter`) para evitar rajadas.
3.  Se um request individual falhar com HTTP 429, o adaptador intercepta, lê o `Retry-After` (suporta segundos e datas RFC 7231), suspende a corrotina com `asyncio.sleep` e tenta novamente (até 3 tentativas).
4.  Se o download for bem-sucedido, as proposições são processadas pelas regras de domínio (identificação de autoria e tema econômico) e persistidas em lote no Postgres via `upsert_em_lote_por_numero_canonico`.

### Fase 5: Ajuste Dinâmico e Telemetria
1.  No fim do lote, o serviço calcula a latência no percentil 95 ($P95$ RTT).
2.  Calibra a taxa e concorrência para o próximo lote (Táticas 2 e 4).
3.  Se os erros 429 definitivos ultrapassarem 20% do lote, o **Circuit Breaker** abre por 30 minutos.
4.  Persiste os novos limites de forma atômica no Redis usando controle de concorrência otimista (`WATCH`/`MULTI`/`EXEC`) e libera o lock do offset.
5.  Emite logs estruturados de telemetria (`[TELEMETRIA BATCH]` e `[TELEMETRIA RESUMO]`).

---

## 4. Mapeamento Detalhado das 4 Táticas Dinâmicas

| Tática | Função | Componentes Envolvidos | Chaves Redis Utilizadas | Impacto e Mitigação |
| :--- | :--- | :--- | :--- | :--- |
| **Tática 1: Pruning** | Evita overhead de COUNTs e consultas externas em anos já preenchidos. | `PreencherLacunasService` | `seeding:consolidado:{fonte}:{ano}:{tipo}` (Históricos)<br>`seeding:sincronizado:ano_atual:{fonte}:{tipo}` (Ano Corrente, TTL 12h) | Reduz o consumo de CPU do banco local e poupa requisições de totalização às APIs em $90\%$. |
| **Tática 2: Concorrência** | Controla as requisições simultâneas via semáforo baseado em latência. | `PreencherLacunasService`, `asyncio.Semaphore` | `seeding:concorrencia:{fonte}` (Câmara: 2 a 20; Senado: 1 a 10) | Evita thundering herd e reduz paralelismo quando a API apresenta lentidão acima de $1.2$ segundos. |
| **Tática 3: Resiliência 429 & CB** | Trata limites de requisição e desliga o worker em caso de falha persistente. | `Adapters`, `PreencherLacunasService` | `seeding:circuit_breaker:{fonte}:estado`<br>`seeding:circuit_breaker:{fonte}:bloqueado_ate` | Garante que o LexTrack respeite limites oficiais (`Retry-After`). O CB abre apenas sob $20\%$ de perdas no lote, evitando reações a falsos positivos. |
| **Tática 4: AIMD & Rate Limiting** | Regula o tamanho máximo de lotes e o tempo mínimo de espaçamento de requests. | `PreencherLacunasService`, `AsyncRateLimiter` | `seeding:taxa:{fonte}` (Câmara: 50 a 300; Senado: 20 a 150) | Algoritmo AIMD aumenta a velocidade de ingestão aditivamente na ausência de erros e corta pela metade de forma agressiva sob falhas de rede/429. |

---

## 5. Mapeamento de Arquivos no Projeto (Onde a Mágica Acontece)

Abaixo está o mapeamento dos arquivos que compõem o sistema de ingestão e resiliência:

```
backend/
├── src/
│   ├── domain/
│   │   ├── exceptions.py ─────────────────── Classe de exceções ricas de rede e status da API
│   │   └── classificacao_preditiva.py ────── Classificadores de poder executivo e tema econômico
│   │
│   ├── application/
│   │   ├── ports/
│   │   │   ├── cache_provider.py ─────────── Porta abstrata para persistência rápida/locks
│   │   │   ├── camara_adapter.py ─────────── Porta abstrata para Câmara
│   │   │   └── senado_adapter.py ─────────── Porta abstrata para Senado
│   │   │
│   │   └── services/
│   │       ├── preencher_lacunas_service.py ── Motor adaptativo de seeds históricos e detecção
│   │       └── detalhe_proposicao_service.py ── Busca sobreposta no banco e APIs externas
│   │
│   └── infrastructure/
│       ├── adapters/
│       │   ├── camara_adapter.py ─────────── Implementação de rede, parser de Retry-After e retries
│       │   └── senado_adapter.py ─────────── Implementação de rede, fallbacks de processo e retries
│       │
│       ├── cache/
│       │   └── redis_client.py ───────────── Execução Lua, SET NX e Controle Otimista (Optimistic Locking)
│       │
│       └── workers/
│           ├── celery_app.py ─────────────── Configuração e agendamento da tarefa a cada 15 min
│           └── coleta_worker.py ──────────── Worker Celery e controle de lock global de overlap
│
└── tests/
    └── unit/
        ├── test_camara_adapter.py ────────── Validação de erros de rede e retries da Câmara
        ├── test_senado_adapter.py ────────── Validação de erros de rede e retries do Senado
        └── test_preencher_lacunas_service.py ── Teste das 4 táticas, calibração e concorrência
```

---

## 6. Mapeamento de Transações Atômicas e Segurança no Redis

Para evitar problemas de colisão, concorrência indevida e vazamento de locks quando múltiplos workers operam simultaneamente, mapeamos e implementamos as seguintes políticas transacionais:

1.  **SET NX para Lock de Bloco**:
    *   A reserva de offset utiliza `set_nx(lock_chave, token, ttl=300)`.
    *   A liberação do lock é feita via script Lua executado atomicamente no Redis:
        ```lua
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        ```
    *   Isso garante que um worker lento **não** apague acidentalmente o lock de outro worker que tenha expirado e assumido o processo.
2.  **Optimistic Locking (WATCH/MULTI/EXEC)**:
    *   Implementado no método `obter_e_atualizar_multichaves_seguro`.
    *   Antes de alterar as taxas de concorrência ou cursor, o Redis observa (`WATCH`) as chaves.
    *   Se outra instância alterar as mesmas chaves concorrentemente, o bloco `EXEC` falha (retorna `None`). O cliente intercepta o `WatchError`, aguarda um tempo aleatório (**Jitter**) e faz até 3 retentativas automáticas sob a mesma disciplina de lock.
    *   Protege contra a regressão do cursor: um cursor só é atualizado se o novo valor for maior que o atual (monotonocidade estrita), exceto no reset deliberado para `0` no ano corrente.

---

## 7. Políticas de Calibração do Agendamento Dinâmico (Opção Híbrida)

O Celery Beat aciona a esteira em intervalo rápido constante (15 minutos). O domínio ajusta dinamicamente a carga de trabalho de acordo com o tamanho do backlog (número total de lacunas ativas pendentes):

1.  **Backlog Ultra-Baixo / Sem Lacunas (`backlog = 0`)**:
    *   **Ação**: Encerra em milissegundos (`early exit`).
    *   **Impacto**: Consumo nulo de recursos.
2.  **Backlog Baixo (`1 a 100` lacunas pendentes)**:
    *   **Ação**: Limita o lote máximo de download a **20 proposições**.
    *   **Impacto**: Mantém sincronização rápida de rotina com baixíssimo impacto nas APIs.
3.  **Backlog Médio (`101 a 1000` lacunas pendentes)**:
    *   **Ação**: Limita o lote máximo de download a **150 proposições**.
    *   **Impacto**: Velocidade moderada para recuperar lacunas pontuais de anos recentes.
4.  **Backlog Alto (`> 1000` lacunas pendentes)**:
    *   **Ação**: Permite a taxa máxima definida pelo AIMD (até **300 proposições**).
    *   **Impacto**: Alto throughput de ingestão para cargas históricas intensivas em larga escala.
