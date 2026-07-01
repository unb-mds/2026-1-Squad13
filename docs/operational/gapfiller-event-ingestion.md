# Guia Operacional - Ingestão de Eventos no Gap-Filler

Este documento orienta os operadores e desenvolvedores do LexTrack sobre a configuração, monitoramento e operação da pipeline de ingestão de eventos integrada ao preenchimento de lacunas de cobertura (Gap-Filler).

## 1. Visão Geral

O Gap-Filler detecta anos em que a cobertura local do banco de dados é inferior a 95% e realiza o preenchimento dessas lacunas trazendo os metadados das proposições. A partir desta entrega, o fluxo foi expandido para suportar o **pós-processamento de eventos (movimentações)** de forma integrada. 

A ingestão de eventos é tratada como **best-effort**: a falha na obtenção das movimentações de uma proposição específica não invalida o salvamento dos metadados da proposição, isolando o erro e permitindo que o lote prossiga normalmente.

## 2. Parâmetros Operacionais e Feature Flag

A ingestão de eventos é controlada por uma feature toggle desativada por padrão e parâmetros operacionais configuráveis sem necessidade de novos deploys.

A precedência para a resolução dos valores de configuração é:
1. **Redis (Chaves dinâmicas)**
2. **Settings / Variáveis de Ambiente (`.env`)**
3. **Valores Padrão no Código**

| Parâmetro | Chave Redis | Variável `.env` | Valor Padrão | Descrição |
|---|---|---|---|---|
| **Habilitar Coleta** | `seeding:enable_eventos_gapfiller` | `GAPFILLER_ENABLE_EVENTOS` | `False` | Habilita/desabilita o pós-processamento de eventos. |
| **Tamanho do Sublote** | `seeding:eventos_batch_size` | `GAPFILLER_EVENTOS_BATCH_SIZE` | `5` | Quantidade de proposições agrupadas por sublote para coleta. |
| **Concorrência** | `seeding:eventos_concorrencia` | `GAPFILLER_EVENTOS_CONCURRENCY` | `5` | Limite de requisições paralelas simultâneas dentro de cada sublote. |

### Exemplo de Configuração via Redis CLI
Para ativar a coleta de eventos e configurar o tamanho de sublote para 10 proposições com concorrência 5:
```bash
redis-cli set seeding:enable_eventos_gapfiller "true"
redis-cli set seeding:eventos_batch_size "10"
redis-cli set seeding:eventos_concorrencia "5"
```

## 3. Logs Estruturados de Execução

As saídas de log do worker são estruturadas em formato machine-readable com tags de identificação para facilitar troubleshooting e monitoramento automático via coletores de log.

### Exemplo de Log de Lote e Início de Sublote (Sucesso)
```text
INFO: [GAPFILLER_EVENTOS_LOTE] Iniciando processamento de 2 proposições. Configuração: batch_size=5, concurrency=5
INFO: [GAPFILLER_EVENTOS_SUBLOTE_INICIO] Processando sublote 1/1 com 2 proposições.
```

### Exemplo de Log de Fim de Sublote
```text
INFO: [GAPFILLER_EVENTOS_SUBLOTE_FIM] Sublote 1/1 finalizado. Elegiveis: 2 | Sucessos: 2 | Falhas: 0
```

### Exemplo de Log com Falhas Parciais Isoladas
Se uma proposição falhar devido a instabilidade externa (timeout ou limite excedido), o erro é registrado no log em nível `ERROR`, mas as outras proposições do sublote seguem seu fluxo:
```text
ERROR: [GAPFILLER_EVENTO_ERRO] Falha ao coletar eventos da proposição camara:12345: Erro de conexão na Câmara
INFO: [GAPFILLER_EVENTOS_SUBLOTE_FIM] Sublote 1/1 finalizado. Elegiveis: 3 | Sucessos: 2 | Falhas: 1
```

## 4. Rollback Operacional (Desabilitação Rápida)

Caso as requisições de eventos provoquem sobrecarga ou acionem Circuit Breakers das APIs externas (Câmara/Senado), a operação pode desabilitar imediatamente a coleta de eventos enviando o valor `"false"` para o Redis. Os workers do Celery lerão a flag dinamicamente e pularão a ingestão de eventos a partir do próximo ciclo de execução.

**Comando de Rollback:**
```bash
redis-cli set seeding:enable_eventos_gapfiller "false"
```

## 5. Procedimento de Monitoramento Mínimo

1. **Checar Atividade**: Filtre logs com a tag `[GAPFILLER_EVENTOS_LOTE]` para validar se a funcionalidade foi acionada.
2. **Avaliar Taxa de Erro**: Monitore o surgimento de logs com a tag `[GAPFILLER_EVENTO_ERRO]`. Se a proporção de falhas/sucessos for muito alta, considere reduzir a concorrência (`seeding:eventos_concorrencia`) ou desativar temporariamente a flag.
3. **Auditoria de Banco**: Verifique no banco se novas linhas estão sendo inseridas na tabela `eventotramitacao` após as execuções bem-sucedidas do Gap-Filler.
