# Plano de Ingestão Incremental — Resiliência e Políticas de Ingestão

Este plano de implementação descreve a evolução da esteira de seeds (preenchimento de lacunas de cobertura) do LexTrack para garantir execução autônoma 24/7 sob estresse de rede, contornando de forma resiliente limites de requisição (HTTP 429), timeouts e falhas nos upstreams (Câmara e Senado).

---

## 1. Objetivo da Implementação

Garantir que a esteira de seeds e preenchimento de lacunas funcione de forma autônoma 24/7 sob estresse de rede, sem risco de banimentos temporários de IP (rate limits) e com visibilidade ponta a ponta dos gargalos operacionais. A execução segue passos incrementais de baixo risco para manter a estabilidade do repositório a cada commit.

---

## 2. Princípios de Execução

1.  **Mudanças Bounded (Reversíveis)**: Cada fase deve ser pequena e testável isoladamente para evitar regressões amplas.
2.  **Isolamento Estrito (Layered Architecture)**: Nenhum detalhe de transporte (HTTP) ou cache/fila (Redis/Celery) deve vazar para a camada de `Domain`. O `Application Service` interage apenas com portas abstratas.
3.  **Segurança Concorrente**: Locks e cursores devem ser protegidos contra colisão via concorrência otimista (WATCH/MULTI/EXEC) no Redis com retentativas e jitter.
4.  **Desacoplamento de Upstreams**: Câmara e Senado operam de forma isolada; a falha de um não deve interromper o fluxo do outro.
5.  **Políticas por Fonte e Endpoint**: Cada upstream tem timeout, retry, backoff, criticidade e budgets próprios.
6.  **Retry Boundado**: Retry local só na infraestrutura; a aplicação não reexecuta a mesma falha em cascata.
7.  **Observabilidade Primeiro**: Sem métricas e correlação, não existe capacidade real de ajuste fino.

---

## 3. Fases de Implementação

### Fase 0 — Baseline e Observabilidade Inicial

*   **Objetivo**: Mensurar e registrar as métricas da esteira atual antes de qualquer alteração de resiliência.
*   **Problemas que resolve**: Falta de visibilidade sobre tempo de resposta (RTT) real, quantidade de timeouts ocorrendo e falhas silenciosas de rede.
*   **Arquivos envolvidos**:
    *   `src/application/services/preencher_lacunas_service.py`
    *   `src/infrastructure/workers/coleta_worker.py`
*   **Dependências**: Nenhuma (usa a estrutura atual de logs).
*   **Riscos se fora de ordem**: Alto. Sem baseline, torna-se impossível quantificar a melhoria trazida pelas próximas fases ou identificar regressões.
*   **Como validar**: Verificar no stdout ou logger do worker se a telemetria inicial de RTT P95 e contagem de erros 429/timeouts está sendo registrada a cada run.
*   **Quando considerar concluída**: Quando a esteira executar por 24 horas em ambiente de testes gravando métricas básicas no logger estruturado.

---

### Fase 1 — Segurança Operacional e Locks

*   **Objetivo**: Evitar overlap de tarefas Celery Beat e redundância de downloads concorrentes do mesmo offset do cursor.
*   **Problemas que resolve**: Thundering herd de workers sobrecarregando o Redis e desperdiçando requisições de rede duplicadas para a mesma página da API oficial.
*   **Arquivos envolvidos**:
    *   `src/application/ports/cache_provider.py`
    *   `src/infrastructure/cache/redis_client.py`
    *   `src/infrastructure/workers/coleta_worker.py`
*   **Dependências**: Conclusão da Fase 0.
*   **Riscos se fora de ordem**: Colisão de cursores e concorrência indevida entre múltiplos workers processando lacunas em paralelo.
*   **Como validar**: Simular duas execuções simultâneas da mesma task Celery e certificar que a segunda aborta informando lock ocupado (`seeding:lock:task_executando`).
*   **Quando considerar concluída**: Quando o lock global de overlap e o lock de offset com token UUID estiverem implantados com sucesso com liberação segura via script Lua.

---

### Fase 2 — Separação de Políticas por Fonte e Endpoint

*   **Objetivo**: Isolar as políticas de conexões, timeouts e retries específicos para a Câmara e para o Senado, bem como seus subfluxos.
*   **Problemas que resolve**: Tratar a Câmara e o Senado como iguais, quando o Senado opera com endpoints muito mais lentos e com fallbacks complexos.
*   **Arquivos envolvidos**:
    *   `src/infrastructure/adapters/camara_adapter.py`
    *   `src/infrastructure/adapters/senado_adapter.py`
*   **Granularidade Fina do Senado**:
    *   `/materia/{id}` (Materia Principal): Timeout 12s, 3 retries, backoff exponencial, criticidade alta (trip do CB se falhas $>20\%$).
    *   `/processo/{id}` (Processo Fallback): Timeout 15s, 2 retries, linear.
    *   `/materia/emendas/{id}` (Emendas): Timeout 6s, 2 retries, backoff flat, criticidade nula (se falhar, ativa a degradação seletiva).
*   **Dependências**: Fase 1.
*   **Riscos se fora de ordem**: Abertura prematura de disjuntores ou timeouts muito longos bloqueando as conexões do pool do worker.
*   **Como validar**: Rodar requisições em ambiente de teste com latência simulada e verificar se os timeouts específicos são disparados corretamente de acordo com a tabela de políticas.
*   **Quando considerar concluída**: Quando os adaptadores Câmara e Senado aplicarem parâmetros de tempo, retry e backoff distintos para cada chamada específica.

---

### Fase 3 — Contratos de Erro e Adaptação

*   **Objetivo**: Traduzir exceções HTTP de baixo nível para exceções de domínio ricas e gerenciar limites de retry nos adaptadores.
*   **Problemas que resolve**: Erros de transporte e status HTTP vazando para a aplicação e causando retry em cascata (adapter + service).
*   **Arquivos envolvidos**:
    *   `src/domain/exceptions.py`
    *   `src/infrastructure/adapters/camara_adapter.py`
    *   `src/infrastructure/adapters/senado_adapter.py`
    *   `src/application/services/preencher_lacunas_service.py`
*   **Dependências**: Fase 2.
*   **Riscos se fora de ordem**: Erro na classificação do Circuit Breaker por não reconhecer a exceção lançada, ou requisições desnecessárias por falta de prelimitação de retry local.
*   **Como validar**: Simular falhas de status 429 e 503 nos testes integrados e verificar se elas chegam à aplicação como `ApiRateLimitError` e `ApiServerError`, respectivamente.
*   **Quando considerar concluída**: Quando todos os adaptadores de rede propagarem exceções de domínio tipadas e o serviço de aplicação gerenciar a telemetria com base nelas.

---

### Fase 4 — Telemetria de Endpoint e Tracing

*   **Objetivo**: Adicionar IDs de correlação a nível de task, lote e requisições HTTP para rastrear a esteira.
*   **Problemas que resolve**: Dificuldade de relacionar uma falha de rede individual a uma execução específica da task Celery ou a um lote de cursor.
*   **Arquivos envolvidos**:
    *   `src/infrastructure/workers/coleta_worker.py`
    *   `src/application/services/preencher_lacunas_service.py`
    *   `src/infrastructure/adapters/camara_adapter.py`
    *   `src/infrastructure/adapters/senado_adapter.py`
*   **Dependências**: Fase 3.
*   **Riscos se fora de ordem**: Baixo. Mas atrasa o diagnóstico de problemas durante a fase de testes e homologação.
*   **Como validar**: Verificar se o log JSON estruturado emite os campos de `correlation_id_task`, `correlation_id_batch` e `frequencia_real_req_s` em todas as runs.
*   **Quando considerar concluída**: Quando qualquer log gerado no fluxo contiver os IDs necessários para rastreabilidade de ponta a ponta.

---

### Fase 5 — Degradação Seletiva e Expiração

*   **Objetivo**: Permitir que o motor degrade de forma suave sem parar o sistema por completo quando endpoints secundários falharem, com expiração automática.
*   **Problemas que resolve**: Queda total da ingestão do Senado por falhas na API de emendas e falta de auto-recuperação do endpoint.
*   **Funcionamento da Expiração**:
    *   Falha consecutiva no endpoint `/materia/emendas` grava `seeding:degradacao:senado:emendas` com TTL de 15 minutos (900 segundos).
    *   Enquanto a chave existir, a chamada ao endpoint de emendas é pulada e `numero_emendas = 0`.
    *   Após 15m a chave expira e o endpoint volta a ser consultado automaticamente.
*   **Arquivos envolvidos**:
    *   `src/infrastructure/adapters/senado_adapter.py`
    *   `src/application/services/preencher_lacunas_service.py`
*   **Dependências**: Fase 4.
*   **Riscos se fora de ordem**: Instabilidades de rede causarem travamento sistemático das tarefas de preenchimento.
*   **Como validar**: Configurar a API de emendas do Senado para falhar e certificar que a matéria principal continua sendo gravada no banco de dados com `numero_emendas = 0` por 15 minutos e volta a ser consultada após a expiração.
*   **Quando considerar concluída**: Quando o sistema continuar operando a Câmara sob colapso do Senado e puder ignorar e auto-recuperar emendas de forma transparente.

---

### Fase 6 — Idempotência e Consistência do Cursor

*   **Objetivo**: Garantir segurança transacional do cursor e proteger o banco de dados contra duplicidades.
*   **Problemas que resolve**: Regressão de cursor no Redis decorrente de concorrência ou crashes do worker, e duplicação de proposições no Postgres.
*   **Arquivos envolvidos**:
    *   `src/infrastructure/repositories/sql_proposicao_repository.py`
    *   `src/application/services/preencher_lacunas_service.py`
*   **Dependências**: Fase 5.
*   **Riscos se fora de ordem**: Inconsistências de dados no banco relacional ou workers processando o passado indefinidamente.
*   **Como validar**: Tentar forçar o salvamento de um cursor menor que o atual e conferir se a transação do Redis (WATCH) bloqueia a escrita.
*   **Quando considerar concluída**: Quando a monotonicidade estiver garantida e os cursores forem persistidos sob disciplina de Optimistic Locking.

---

### Fase 7 — Testes e Homologação de Resiliência

*   **Objetivo**: Criar a suite de testes automatizados simulando condições reais de falhas e estresse de infraestrutura.
*   **Problemas que resolve**: Regressões em manutenções futuras causadas por falta de cobertura de testes.
*   **Arquivos envolvidos**:
    *   `tests/unit/test_preencher_lacunas_service.py`
    *   `tests/unit/test_camara_adapter.py`
    *   `tests/unit/test_senado_adapter.py`
*   **Dependências**: Conclusão de todas as fases de código (1 a 6).
*   **Riscos se fora de ordem**: Falta de mocks estáveis para testar comportamentos dinâmicos complexos como AIMD e CB.
*   **Como validar**: Executar `pytest tests/unit/test_preencher_lacunas_service.py` e certificar cobertura verde.
*   **Quando considerar concluída**: Quando a taxa de cobertura de testes para a lógica do motor de seeding atingir mais de 90%.

---

## 4. Arquivos a Criar ou Modificar

```
backend/
├── src/
│   ├── domain/
│   │   └── exceptions.py [MODIFY] (Enriquecer exceções ApiException, ApiRateLimitError, etc)
│   │
│   ├── application/
│   │   ├── ports/
│   │   │   └── cache_provider.py [MODIFY] (Adicionar assinaturas de set_nx, eval_lua, obter_e_atualizar)
│   │   │
│   │   └── services/
│   │       └── preencher_lacunas_service.py [MODIFY] (Integrar P95, calibração de backlog, e telemetria)
│   │
│   └── infrastructure/
│       ├── adapters/
│       │   ├── camara_adapter.py [MODIFY] (Timeouts, retries locais, e exceções de domínio)
│       │   └── senado_adapter.py [MODIFY] (Timeout por endpoint, fallbacks de processo, e exceções)
│       │
│       ├── cache/
│       │   └── redis_client.py [MODIFY] (Transações com WATCH/MULTI/EXEC, Lua release, e retries com jitter)
│       │
│       └── workers/
│           ├── celery_app.py [MODIFY] (Mudar frequência do beat para minuto="*/15")
│           └── coleta_worker.py [MODIFY] (Prevenção de overlap e lock global)
│
└── tests/
    └── unit/
        └── test_preencher_lacunas_service.py [MODIFY] (Novos testes de backlog e CB)
```

---

## 5. Testes por Fase

*   **Fase 1 (Locks)**: `test_cursor_reserva_lock` e `test_overlap_prevention_on_worker`.
*   **Fase 2 & 3 (Políticas & Exceções)**: `test_camara_adapter_erro_rede`, `test_senado_adapter_erro_rede` e `test_429_com_retry_after` (validando parse).
*   **Fase 5 (Degradação)**: `test_degradacao_senado_emendas_graceful` (simulando timeout em emendas e checando se a matéria principal é gravada com 0 emendas).
*   **Fase 6 (Consistência)**: `test_cursor_commit_monotonicidade` (garante que cursor não regrida).

---

## 6. Riscos e Trade-offs

1.  **Overhead de Rede do Redis**:
    *   *Risco*: Consultar o Redis com muita frequência no loop de ticks ou para locks pequenos pode gerar gargalo de rede.
    *   *Mitigação*: Lógica "Read Once / Update Once" garante que o Redis seja acessado apenas no início e fim do lote.
2.  **Carga no Postgres**:
    *   *Risco*: Upserts em lote muito frequentes a cada 15 minutos sob backlog alto podem concorrer com o dashboard do usuário.
    *   *Mitigação*: A calibração de volume por backlog (cap de 20 e 150) suaviza o impacto no Postgres conforme o sistema se estabiliza.

---

## 7. Critérios de Aceite e Vínculo com Observabilidade

Cada critério de aceite operacional deve ser verificado diretamente através dos logs ou métricas coletadas:

| Critério de Aceite | Validação de Log / Métrica | Ação Corretiva se Falhar |
| :--- | :--- | :--- |
| **1. Prevenção de Overlap** | O log indica `⏭️ Task de preenchimento de lacunas já em andamento. Abortando.` se acionado simultaneamente. | Reduzir o TTL do lock global de 30m para 15m. |
| **2. Calibração de Volume** | Log `[TELEMETRIA BATCH]` apresenta `Throughput Atual` capped em 20 se backlog $\le 100$, e 150 se backlog $\le 1000$. | Conferir a contagem total no Postgres e a lógica no Service. |
| **3. Circuit Breaker** | Emissão do log `[BREAKER_OPENED_429]` quando a taxa de 429 definitivos excede 20% do lote total. | Revisar os contadores de erro na resposta do `asyncio.gather`. |
| **4. Degradação Seletiva** | Emissão de warning `⚠️ Senado com API de emendas degradada. Ignorando endpoint por 15m.` e persistência com `numero_emendas = 0`. | Validar se a chave `seeding:degradacao:senado:emendas` foi criada com TTL de 900s. |
| **5. Expiração de Degradação** | Chave `seeding:degradacao:senado:emendas` deixa de existir após 15m e o log do lote subsequente volta a registrar `numero_emendas` válidos. | Inspecionar a expiração via `TTL` no redis-cli. |
| **6. Monotonicidade do Cursor** | Inexistência do log `[CURSOR_REGRESSAO_BLOQUEADA]` durante o fluxo normal. | Auditar a transação de WATCH no RedisClient. |

---

## 8. Recomendação Final

Inicie a execução rigorosamente pela **Fase 1 (Locks)** para blindar a infraestrutura Celery contra sobreposição, e em seguida configure as **Fases 2 e 3 (Políticas & Exceções)** para isolar o comportamento de rede. Esta abordagem garante que o sistema seja robusto e previsível antes de adicionarmos telemetria fina e regras de degradação mais avançadas.
