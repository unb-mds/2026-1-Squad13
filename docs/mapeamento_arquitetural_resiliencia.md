# Mapeamento Arquitetural de Resiliência e Políticas de Ingestão (Seeds)

Este documento estabelece o mapeamento arquitetural sênior para as políticas de resiliência, budgets de tempo, observabilidade e estratégias de degradação seletiva do motor de preenchimento de lacunas (seeds históricos) do LexTrack.

---

## 1. Visão Geral do Desenho

A robustez da esteira de ingestão se apoia na divisão estrita de responsabilidades entre as camadas do sistema, garantindo isolamento absoluto de regras de negócio em relação a tecnologias de rede ou banco de dados.

```
┌────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION                               │
│  - Orquestra a detecção de lacunas e prioridades.                      │
│  - Toma decisões de negócio sobre "onde buscar" e "quando parar".      │
│  - Calcula as métricas P95 RTT agregadas por lote.                     │
│  - Calibra o tamanho dos lotes e limites do Semáforo (AIMD).           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                                 DOMAIN                                 │
│  - Define a taxonomia de erros através de exceções ricas.             │
│  - Executa as regras de validação estrutural de Proposições.           │
│  - Determina criticidade de dados (ex: emendas não barram a run).      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                             INFRASTRUCTURE                             │
│  - Executa as chamadas HTTP e intercepta erros reais de transporte.    │
│  - Implementa retries e backoffs locais com leitura de Retry-After.    │
│  - Traduz status HTTP em exceções de domínio (ApiRateLimitError, etc). │
│  - Gerencia locks e persistência real (RedisClient / PostgreSQL).      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Matriz de Políticas por Fonte e Endpoint

As APIs da Câmara e do Senado operam com arquiteturas e limites de concorrência completamente distintos. Por esta razão, cada endpoint possui regras dedicadas de timeout, retry e criticidade para o acionamento do Circuit Breaker:

| Fonte / Endpoint | Timeout por Chamada | Máximo de Tentativas | Tipo de Backoff | Criticidade para CB | Tratamento de 429 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Câmara - Listagem** (`/proposicoes`) | 10s | 3 | Exponencial + Jitter | **Média** (Apenas falhas repetidas barram a run) | Respeita `Retry-After` ou aplica recuo. |
| **Câmara - Detalhe** (`/proposicoes/{id}`) | 8s | 3 | Exponencial + Jitter | **Alta** (Se $> 20\%$ de erros 429 no lote, abre CB) | Respeita `Retry-After` de forma estrita. |
| **Senado - Listagem** (`/processo`) | 12s | 3 | Exponencial + Jitter | **Média** (Falha barra o lote) | Respeita `Retry-After` ou aplica recuo. |
| **Senado - Matéria** (`/materia/{id}`) | 12s | 3 | Exponencial | **Alta** (Se $> 20\%$ falhar, abre CB) | Respeita `Retry-After` de forma estrita. |
| **Senado - Processo** (`/processo/{id}`) | 15s | 2 | Linear Simples | **Média** (Endpoint de fallback caso Matéria dê 404) | Respeita `Retry-After`. |
| **Senado - Emendas** (`/materia/emendas/{id}`) | 6s | 2 | Sem Backoff | **Nula** (Se falhar, assume 0 emendas e prossegue) | Ignora ou recua 1s fixo. |

---

## 3. Budgets de Tempo e Retries

### A. Hierarquia de Budgets (Timeouts)
*   **Budget por Request**: Controlado localmente nos adaptadores (de 6s a 15s dependendo do endpoint).
*   **Budget por Lote (Batch Gather)**: Controlado no `PreencherLacunasService` via `asyncio.gather`. O tempo limite do lote é de **90s** (se ultrapassar, a execução do lote é cancelada para evitar travamento de workers).
*   **Budget por Execução da Task Celery**: Configurado como limite de tempo físico da tarefa Celery (`time_limit=1800` (30 minutos) e `soft_time_limit=1500`). O TTL do lock global de overlap é de **30 minutos**.

### B. Regras de Retentativa (Retry)
*   **O que DEVE ser retryado**:
    *   Erros de Rede/Conexão transientes (`ApiConnectionError`).
    *   Timeouts de leitura ou conexão (`ApiTimeoutError`).
    *   Erros de Servidor Upstream (`ApiServerError` - 502, 503, 504).
    *   Erros de limite de requisição (`ApiRateLimitError` - 429).
*   **O que NÃO DEVE ser retryado**:
    *   Status `404 Not Found` (indica ausência real do recurso ou necessidade de fallback de endpoint).
    *   Status `400 Bad Request` (erro de formatação de parâmetro pelo cliente).
    *   Status `422 Unprocessable Entity` (problema estrutural de payload).

### C. Prevenção de Retry em Cascata
Para evitar o efeito de amplificação de carga sob estresse (onde o adaptador retenta $3\times$ e o serviço orquestrador também retenta $3\times$, totalizando $9\times$ requisições para a mesma falha):
*   **Decisão**: O adaptador executa o retry local (até 3 tentativas). Se todas falharem, ele lança a exceção de domínio. O `PreencherLacunasService` **não** realiza novas retentativas daquela proposição individual. O erro é contabilizado para as estatísticas do lote e o disjuntor decide se abre ou não.

---

## 4. Observabilidade e Telemetria

Para diagnosticar gargalos de forma precisa em produção, todo o fluxo de execução é rastreado por meio de identificadores únicos (Correlation IDs) e métricas acumuladas:

```
[Celery Beat] ──► Gera Correlation ID (Task)
                    │
                    ├──► [Service Run] ──► Gera Correlation ID (Batch/Lote)
                                            │
                                            └──► [Adapter HTTP Call] ──► Header: X-Request-ID
```

### Campos Mínimos para Logs Estruturados (`JSON format`)
```json
{
  "timestamp": "2026-06-13T01:15:00.000Z",
  "level": "INFO",
  "logger": "application.services.preencher_lacunas_service",
  "message": "[TELEMETRIA BATCH] Processamento concluído",
  "correlation_id_task": "a3b8-91f2-...",
  "correlation_id_batch": "lote-camara-2026-PL",
  "fonte": "camara",
  "ano": 2026,
  "tipo": "PL",
  "rtt_p95_ms": 380,
  "frequencia_real_req_s": 5.26,
  "concorrencia_limite": 11,
  "throughput_itens_lote": 20,
  "erros_429": 0,
  "erros_5xx": 0,
  "erros_timeout": 0,
  "offset_anterior": 240,
  "offset_novo": 260
}
```

---

## 5. Idempotência e Segurança de Reexecução

A esteira de seeds foi desenhada para ser totalmente tolerante a falhas no meio do processo e reexecuções arbitrárias:

1.  **Persistência Idempotente (PostgreSQL)**:
    *   Toda gravação utiliza operações de `UPSERT` baseadas na chave primária de ID oficial da proposição e no código canônico (`tipo-numero-ano`).
    *   Se a mesma proposição for reinserida, o banco atualiza os campos de movimentações e status mais recentes, evitando duplicidade de registros.
2.  **Locks com Dono (Ownership Tokens)**:
    *   O lock de reserva de offset de cursor é escrito com chave única: `seeding:lock:processando:{fonte}:{ano}:{tipo}:{offset}`.
    *   O valor gravado é um UUID gerado aleatoriamente pelo worker ativo.
    *   A liberação do lock é realizada através de um script Lua atômico que verifica se o token fornecido confere com o armazenado no Redis. Isso previne que um worker lento destrua o lock de outro worker que tenha assumido após expiração do TTL de 5 minutos.

---

## 6. Estratégias de Degradação Seletiva

Sob condições extremas de lentidão ou indisponibilidade, o motor desliga recursos secundários para manter o sistema operacional:

1.  **Isolamento de Fonte**:
    *   Se a API da Câmara estiver instável (CB aberto), o Senado continua processando seu backlog de forma independente (e vice-versa).
2.  **Degradação de Endpoint (Graceful Fallback)**:
    *   Se as requisições de emendas do Senado (`/materia/emendas`) apresentarem taxa de timeout alta ou RTT lento, o adaptador suspende a busca de emendas por 15 minutos, definindo `numero_emendas = 0` na entidade criada. O preenchimento das matérias principais prossegue normalmente.
3.  **Calibração por Backlog**:
    *   Caso a latência média (RTT P95) ultrapasse **1.5 segundos**, o tamanho do lote de download é reduzido automaticamente pela metade e o semáforo de concorrência é cortado ao mínimo, preservando a estabilidade da esteira.

---

## 7. Testes de Contrato e Resiliência

Para validar e garantir o correto funcionamento das políticas estabelecidas neste plano, implementamos os seguintes testes de resiliência:

*   **Testes de Circuit Breaker**: Simulam falha crônica de 429 definitiva acima de 20% do lote, verificando a transição do estado do disjuntor para `OPEN`.
*   **Testes de Retry-After**: Validam o parse de datas RFC 7231 e a suspensão da corrotina com base no tempo de recuo do cabeçalho.
*   **Testes de Monotonicidade do Cursor**: Garantem que o cursor nunca retroceda para valores menores, exceto no reset intencional do ano corrente.
*   **Testes de Degradação Seletiva**: Validam o comportamento de falha graciosa (ex: 0 emendas sob timeout na API de emendas).

---

## 8. Riscos e Trade-offs

1.  **Polimento Excessivo do Semáforo (Thrashing)**:
    *   *Risco*: Ajustar limites de concorrência a cada requisição pode gerar overhead de escrita no Redis.
    *   *Mitigação*: Os limites de concorrência e throughput só são recalculados e salvos de forma atômica **uma única vez ao final de cada lote**.
2.  **Timeouts Excessivamente Longos**:
    *   *Risco*: Aguardar 15 segundos para fallbacks do Senado pode segurar conexões em aberto.
    *   *Mitigação*: O pool de conexões do `httpx.AsyncClient` é fechado de forma estrita via `finally` após a conclusão do lote, prevenindo vazamento de sockets.

---

## 9. Recomendação Final

O agendamento com a **Opção Híbrida** (Beat de 15 min + Volume Calibrado no Domínio) é a escolha mais aderente a ambientes de produção de alta concorrência. Ela mantém a simplicidade de infraestrutura do Celery Beat padrão e delega toda a inteligência e adaptação matemática (AIMD, CB e calibração de backlog) para o serviço da aplicação, garantindo que o LexTrack se comporte como um cliente bem-educado e extremamente resiliente em relação às APIs públicas.
