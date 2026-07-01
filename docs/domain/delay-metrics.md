# Especificação de Métricas de Atraso e Classificação de Proposições

## 1. Objetivo e Princípios

Esta especificação define como implementar as métricas de atraso de tramitação e a classificação de proposições como atrasadas no sistema de monitoramento legislativo. O processo legislativo brasileiro é complexo e varia por tipo de proposição, fase e regime de tramitação, de modo que a métrica não utiliza apenas dias absolutos, mas sim um índice relativo ao comportamento histórico de grupos comparáveis.

### Princípios de Produto
A implementação atende três superfícies principais:
- **Dashboard**: Agregações, ranking de gargalos e distribuição por faixas de atraso.
- **Aba de Proposições**: Filtros por status, ordenação e badges visuais.
- **Detalhamento**: Explicação do motivo do atraso (fase crítica) e comparação com baselines.

### Referências de Código
*   **Regras de Domínio (Cálculo)**: [CalcularMetricasService](file:///home/caio_martins/2026-1-Squad13/backend/src/domain/services/calcular_metricas_service.py)
*   **Orquestração de Baseline**: [RecalcularBaselinesService](file:///home/caio_martins/2026-1-Squad13/backend/src/application/services/recalcular_baselines_service.py)

---

## 2. Métricas Oficiais

A plataforma utiliza três métricas fundamentais para diagnosticar o ritmo de uma matéria:

### 2.1. Índice de Atraso Relativo (IAR)
Métrica principal de classificação. Mede quanto tempo a proposição levou (ou já levou) em comparação com o tempo esperado de um grupo comparável.

$$
IAR = \frac{T_{decorrido}}{T_{esperado\_grupo}}
$$

*   **T_decorrido**: Dias desde a apresentação até hoje (se ativa) ou até o desfecho (se encerrada).
*   **T_esperado_grupo**: Mediana histórica do tempo total de proposições com o mesmo `tipo` e `regime_tramitacao`.

### 2.2. Índice de Atraso da Fase Atual (IAF)
Métrica diagnóstica que explica o tempo gasto na fase corrente em relação à expectativa para aquela fase.

$$
IAF = \frac{T_{fase\_atual\_real}}{T_{fase\_atual\_esperado}}
$$

*   **T_fase_atual_real**: Tempo acumulado na ocorrência ativa da fase atual.
*   **T_fase_atual_esperado**: Mediana histórica da duração daquela fase para o grupo comparável.

### 2.3. Índice de Espera Improdutiva (IEI)
Métrica diagnóstica que mede a proporção do tempo total que ocorreu sem avanço significativo (inércia).

$$
IEI = \frac{T_{espera\_improdutiva}}{T_{decorrido}}
$$

Um evento é considerado "espera improdutiva" se não for deliberativo, não mudar a fase e não mudar o órgão da proposição.

---

## 3. Classificação de Status de Atraso

Com base no **IAR**, cada proposição é classificada em uma das seguintes categorias:

| Status | Faixa de IAR | Significado Visual |
| :--- | :--- | :--- |
| `NO_PRAZO` | $IAR < 1.0$ | Trâmite mais rápido que a mediana. |
| `ATENCAO` | $1.0 \le IAR < 1.5$ | Trâmite em transição aceitável. |
| `ATRASADA` | $1.5 \le IAR < 2.5$ | Tempo excedido em mais de 50%. |
| `CRITICA` | $IAR \ge 2.5$ | Matéria com atraso severo (> 2.5x). |
| `INSUFICIENTE_BASELINE` | N/A | Falta de dados mínimos para calibração. |

---

## 4. Arquitetura de Baselines (Híbrida)

Para lidar com a falta inicial de massa histórica (especialmente em novos sistemas), a plataforma utiliza uma estratégia de três camadas:

1.  **Baseline Histórico Dinâmico**: Calculado a partir dos dados reais do banco local quando houver amostra suficiente ($n \ge 30$).
2.  **Baseline de Bootstrap Seed**: Utiliza estimativas empíricas calibradas (pré-populadas no sistema).
3.  **Fallback Regimental**: Aplica prazos genéricos baseados nos regimentos internos (RICD/RISF) ou Constituição.

### Estratégia de Fallback Sem Dimensão "Tema"
Dado que a dimensão `tema` não é utilizada estruturalmente na fase atual, o fallback segue a ordem:
1. `tipo` + `regime_tramitacao` + `casa_iniciadora`.
2. `tipo` + `regime_tramitacao` (Simplificação de Origem).
3. Consumo de Bootstrap Seed.

---

## 5. Modelo de Dados

### 5.1. Extensão da Tabela `proposicao` ([ProposicaoModel](file:///home/caio_martins/2026-1-Squad13/backend/src/infrastructure/database/models/proposicao_model.py))
Campos para persistência das métricas calculadas:
* `indice_atraso_relativo` (numeric)
* `indice_atraso_fase_atual` (numeric)
* `indice_espera_improdutiva` (numeric)
* `status_atraso` (string)
* `dias_decorridos_total` (integer)
* `dias_esperados_total` (integer)
* `baseline_grupo_id` (string)
* `data_calculo_metricas` (datetime)

### 5.2. Tabela `baseline_tramitacao` ([BaselineTramitacaoModel](file:///home/caio_martins/2026-1-Squad13/backend/src/infrastructure/database/models/baseline_tramitacao_model.py))
Tabela que armazena tanto sementes fixas quanto cálculos dinâmicos:

| Campo | Descrição |
| :--- | :--- |
| `baseline_id` | Identificador único (PK). |
| `escopo` | `TOTAL` (para IAR) ou `FASE` (para IAF). |
| `tipo` | Ex: 'PL', 'PEC', 'MPV'. |
| `regime_tramitacao` | Ex: 'ORDINARIO', 'URGENCIA'. |
| `fase_codigo` | Código da fase (nulo se escopo for TOTAL). |
| `mediana_dias` | O valor de referência em dias. |
| `origem_dados` | `DYNAMIC_CALCULATION` ou `BOOTSTRAP_SEED`. |

---

## 6. Calibração Inicial (Bootstrap Seeds)

### Baselines de Escopo TOTAL (IAR) Sugeridos:
| Tipo | Regime | Mediana Esperada | Justificativa |
| :--- | :--- | :--- | :--- |
| **PL** | `ORDINARIO` | 730 dias (2 anos) | Mediana empírica do Congresso. |
| **PL** | `URGENCIA` | 90 dias | Prazo constitucional (Art. 64 CF). |
| **PEC** | `ORDINARIO` | 1095 dias (3 anos) | Rito especial complexo em dois turnos. |
| **MPV** | `ORDINARIO` | 60 dias | Vigência inicial (Art. 62 CF). |

### Baselines de Escopo FASE (IAF) Sugeridos:
* **ANALISE_COMISSOES (PL Ordinário)**: 180 dias.
* **ETAPA_EXECUTIVO (Qualquer)**: 15 dias úteis (Prazo constitucional de sanção/veto).
* **PROTOCOLO_INICIAL**: 15 dias.

---

## 7. Pipeline de Implementação

1.  **Carga Inicial**: Executar script SQL de Bootstrap Seeds na migração do banco.
2.  **Job de Cálculo**: Processar métricas de todas as proposições ativas.
3.  **API de Listagem**: Expor `status_atraso` e `indice_atraso_relativo`.
4.  **API de Detalhe**: Expor diagnóstico completo (`indice_atraso_fase_atual` e `indice_espera_improdutiva`).
5.  **Job Diário**: Recalcular baselines dinâmicos conforme a base de dados cresce.
