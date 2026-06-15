# Guia de Monitoramento, Logs e Validação do Seeding Adaptativo

Este documento serve como um guia operacional (Playbook) para desenvolvedores e administradores do LexTrack monitorarem a saúde, depurarem problemas e validarem o correto funcionamento do motor de preenchimento de lacunas (seeds).

---

## 1. Padrões de Log e Telemetria

O motor de seeding foi projetado para emitir logs estruturados e fáceis de filtrar. Existem duas principais linhas de log emitidas sob a tag `[TELEMETRIA]`:

### A. Telemetria de Lote (`[TELEMETRIA BATCH]`)
Emitida sempre que um lote individual de proposições de uma fonte é concluído (seja com sucesso total ou parcial).

*   **Exemplo de Log**:
    ```text
    INFO: [TELEMETRIA BATCH] Fonte: camara | Lacuna: 2026:PL | Processados: 18/20 | RTT P95: 380ms | Frequência Real: 5.26 req/s | Limite Semáforo: 11 | Throughput Atual: 20 itens/lote | Erros: [429_count: 0] [5xx_count: 0] [timeout_count: 0] | Max Retry-After: 0s | Cursor: 240 -> 260
    ```

*   **Significado dos Campos**:
    *   `Fonte`: A API de origem (`camara` ou `senado`).
    *   `Lacuna`: O ano e tipo de proposição sendo processados (`ANO:TIPO`).
    *   `Processados`: Quantas proposições foram gravadas com sucesso no Postgres em relação ao número solicitado (`gravados/solicitados`).
    *   `RTT P95`: A latência no percentil 95 observada nas requisições HTTP deste lote.
    *   `Frequência Real`: A velocidade real medida em requisições por segundo (`req/s`) durante a execução paralela do lote.
    *   `Limite Semáforo`: O limite de concorrência atual do `asyncio.Semaphore` (Tática 2).
    *   `Throughput Atual`: O tamanho do lote atual em quantidade de proposições (`itens/lote`), calibrado pelo backlog e AIMD.
    *   `Erros`: Contadores de falhas temporárias interceptadas durante a execução do lote (`429_count`, `5xx_count`, `timeout_count`).
    *   `Max Retry-After`: O maior tempo de cooldown em segundos exigido pela API externa neste lote.
    *   `Cursor`: O avanço monotônico do offset do cursor (`anterior -> novo`).

### B. Telemetria de Resumo (`[TELEMETRIA RESUMO]`)
Emitida ao final de cada execução global do Celery Worker, sintetizando o estado de todas as fontes no Redis.

*   **Exemplo de Log**:
    ```text
    INFO: [TELEMETRIA RESUMO] Status da Run: catch_up
     - Câmara: [Estado CB: CLOSED] [Throughput Alvo: 80 itens/lote] [Concorrência: 10] [Falhas Run: 429=0, 5xx=0, timeouts=0] [RTT P95: 350ms]
     - Senado: [Estado CB: OPEN] [Throughput Alvo: 20 itens/lote] [Concorrência: 2] [Falhas Run: 429=3, 5xx=0, timeouts=1] [RTT P95: 1850ms]
    ```

*   **Significado dos Campos**:
    *   `Status da Run`: `catch_up` (ingerindo dados) ou `manutencao` (backlog zerado, sem novas lacunas).
    *   `Estado CB`: O estado do Circuit Breaker (`CLOSED`, `OPEN` ou `HALF-OPEN`).
    *   `Throughput Alvo`: A taxa/tamanho máximo de lote calculado pelo algoritmo AIMD (Tática 4), em `itens/lote`.
    *   `RTT P95`: Percentil 95 global acumulado de RTT para a fonte.

---

## 2. Comandos Úteis para Visualização de Logs (CLI)

Use estes comandos no terminal para inspecionar o comportamento do worker Celery em tempo real:

### Filtrar apenas a Telemetria
Para monitorar a velocidade de ingestão e a saúde das chamadas:
```bash
docker compose logs -f celery_worker | grep "\[TELEMETRIA"
```

### Monitorar o Circuit Breaker
Para verificar aberturas, fechamentos e períodos de teste (`HALF-OPEN`):
```bash
docker compose logs -f celery_worker | grep -E "\[BREAKER|disjuntor"
```

### Acompanhar o Movimento dos Cursores
Para garantir que os cursores estão avançando de forma monotônica ou resetando corretamente:
```bash
docker compose logs -f celery_worker | grep -E "\[CURSOR|Resetando cursor"
```

### Identificar Sinais de Saturação (HTTP 429 / Timeouts)
Para investigar gargalos e rate-limits:
```bash
docker compose logs -f celery_worker | grep -iE "429|too many|timeout|backoff"
```

---

## 3. Validação do Estado no Redis (`redis-cli`)

Para inspecionar o estado em tempo real armazenado pelo LexTrack no Redis, acesse o terminal do container do Redis:
```bash
docker compose exec redis redis-cli
```

### Consultas de Estado Comuns:

*   **Verificar se a tarefa está rodando no momento (Lock de Overlap)**:
    ```bash
    GET seeding:lock:task_executando
    ```
    *(Se retornar `nil`, nenhuma task está rodando no momento. Se retornar um UUID, a execução está ativa).*

*   **Checar Estado do Circuit Breaker por Fonte**:
    ```bash
    GET seeding:circuit_breaker:camara:estado
    GET seeding:circuit_breaker:camara:bloqueado_ate
    ```

*   **Verificar Throughput (AIMD) e Concorrência atuais**:
    ```bash
    GET seeding:taxa:camara
    GET seeding:concorrencia:camara
    ```

*   **Consultar Cursor de um Ano/Tipo específico**:
    ```bash
    GET seeding:cursor:camara:2026:PL
    ```

*   **Listar todos os Anos Consolidados (Pruning)**:
    ```bash
    KEYS seeding:consolidado:*
    ```

---

## 4. Diagnóstico de Gargalos e Resolução de Problemas

Use a tabela abaixo para diagnosticar comportamentos inesperados observados nos logs:

| Sintoma Visualizado nos Logs | Causa Provável | Diagnóstico e Ação Corretiva |
| :--- | :--- | :--- |
| **Throughput travado no mínimo** (`taxa:camara` = 50, `taxa:senado` = 20) | Resposta persistente de erro 429 ou timeouts sucessivos. | 1. Verifique se a API externa está fora do ar ou se houve alteração na chave de API.<br>2. Verifique se o log exibe `⏳ API retornou 429. Aguardando Retry-After...`<br>3. Se a lentidão for geral na infraestrutura, a latência P95 RTT alta manterá o semáforo e a taxa no mínimo de forma legítima. |
| **Circuit Breaker entra em `OPEN` constantemente** | Falhas de rede massivas ou rate-limit severo que excede 20% do lote. | 1. Verifique os logs de conexão (`🔌 Falha de rede na Câmara`). Se o container estiver sem DNS ou internet, o CB abrirá por 15m após 5 falhas consecutivas.<br>2. Se o CB abrir com tag `[BREAKER_OPENED_429]`, o rate limit excedeu a tolerância do Retry-After. Reduza o `TAXA_MAX` no service se necessário. |
| **Cursor não avança entre runs** | Falha crítica de listagem de IDs ou colisão concorrente de cursor. | 1. Verifique se há erros na listagem inicial (`Erro ao listar recentes`). Se a listagem falhar por completo, o cursor não é comitado.<br>2. Verifique se o log exibe `⏭️ Offset ... já reservado`. Isso indica que outro worker está processando o mesmo lote e a execução atual pulou o offset de forma segura. |
| **Tarefa de Ingestão passa a retornar `Status da Run: manutencao`** | O backlog de lacunas foi completamente preenchido. | **Sucesso operacional**. O banco local possui mais de 95% de cobertura de todas as proposições desde 1988. O sistema monitorará em modo de baixo consumo apenas o ano atual. |
