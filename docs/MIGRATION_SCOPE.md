# MIGRATION_SCOPE.md — Refatoração do Modelo de Tramitação

**Branch:** `feat/escopo-tramitacao-analitica`  
**Decisão de escopo:** substituir o modelo raso de `Tramitacao` por um modelo analítico
capaz de medir tempo por fase, identificar gargalos e servir de base para o R2.  
**Dados atuais:** apenas seed — drop seguro, sem perda de dados reais.

---

## O que muda

### Tabelas removidas

| Tabela | Motivo |
|---|---|
| `tramitacao` | Substituída por `evento_tramitacao` com campos analíticos |

### Tabelas criadas

| Tabela | Responsabilidade |
|---|---|
| `fase_analitica` | Lookup das 8 fases do processo legislativo |
| `orgaolegislativo` | Cadastro normalizado de comissões e plenário |
| `evento_tramitacao` | Substitui `tramitacao` — cada movimentação com tipo e fase normalizados |

### Tabelas mantidas (sem alteração estrutural)

| Tabela | Observação |
|---|---|
| `proposicao` | Sem mudança de campos neste PR |
| `usuario` | Sem alteração |

---

## Mapeamento de campos: Tramitacao → EventoTramitacao

| Campo atual (`tramitacao`) | Destino (`evento_tramitacao`) | Observação |
|---|---|---|
| `id` | `evento_id` | Renomeado para consistência |
| `proposicao_id` | `proposicao_id` | FK mantida |
| `data_hora` | `data_evento` | Renomeado |
| `sequencia` | `sequencia` | Mantido |
| `sigla_orgao` | `sigla_orgao` | Mantido — também resolve FK para `orgaolegislativo` |
| `descricao_tramitacao` | `descricao_original` | Renomeado — guarda o texto bruto da API |
| `despacho` | `descricao_original` | Consolidado no mesmo campo |
| `status` | *(removido)* | Substituído por `tipo_evento` normalizado |
| *(não existia)* | `tipo_evento` | **Novo** — enum com 19 tipos normalizados |
| *(não existia)* | `fase_analitica_id` | **Novo** — FK para `fase_analitica` |
| *(não existia)* | `deliberativo` | **Novo** — boolean: votação ou decisão? |
| *(não existia)* | `mudou_fase` | **Novo** — controle analítico |
| *(não existia)* | `mudou_orgao` | **Novo** — controle analítico |
| *(não existia)* | `remessa_ou_retorno` | **Novo** — trânsito entre Casas |
| *(não existia)* | `payload_bruto` | **Novo** — JSON original da API para auditoria |

---

## Mapeamento de campos: Proposicao → campos afetados

A entidade `Proposicao` não muda estruturalmente neste PR. Os campos abaixo
eram calculados em memória pelo `DashboardService` — passam a ser calculados
a partir de `evento_tramitacao`:

| Campo / cálculo atual | Novo origem |
|---|---|
| `tempo_total_dias` (calculado em memória) | delta entre primeiro `APRESENTACAO` e evento terminal em `evento_tramitacao` |
| `atraso_critico` (flag booleano) | derivado do cálculo acima (> 180 dias) |
| `status_atual` | último `tipo_evento` da sequência |

---

## Fases analíticas (seed fixo)

Estas 8 linhas são inseridas no seed antes de qualquer proposição.
Nunca são criadas em runtime.

| codigo | nome | ordem_logica |
|---|---|---|
| `PROTOCOLO_INICIAL` | Protocolo inicial | 1 |
| `ANALISE_COMISSOES` | Análise em comissões | 2 |
| `AGUARDANDO_PAUTA` | Aguardando pauta | 3 |
| `DELIBERACAO_PLENARIO` | Deliberação em plenário | 4 |
| `TRAMITE_ENTRE_CASAS` | Trâmite entre Casas | 5 |
| `REVISAO_OUTRA_CASA` | Revisão na outra Casa | 6 |
| `ETAPA_EXECUTIVO` | Etapa no Executivo | 7 |
| `ENCERRADA` | Encerrada | 8 |

---

## Tipos de evento normalizados (enum)

20 tipos usados em `EventoTramitacao.tipo_evento`:

`APRESENTACAO` · `DESPACHO` · `RECEBIMENTO_ORGAO` · `DESIGNACAO_RELATOR`
· `PARECER` · `INCLUSAO_PAUTA` · `RETIRADA_PAUTA` · `VOTACAO_COMISSAO`
· `VOTACAO_PLENARIO` · `APROVACAO` · `REJEICAO` · `REMESSA_OUTRA_CASA`
· `RECEBIMENTO_OUTRA_CASA` · `RETORNO_INICIADORA` · `ARQUIVAMENTO`
· `PREJUDICIALIDADE` · `ENVIO_EXECUTIVO` · `SANCAO_OU_VETO` · `PROMULGACAO`
· `NAO_CLASSIFICADO`

> **Nota sobre `NAO_CLASSIFICADO`:** tipo de fallback usado quando nenhum pattern
> da função `classificar_tipo_evento()` casar com a descrição original da API.
> Motivação: usar `DESPACHO` como fallback contaminaria métricas de tempo por fase.
> `NAO_CLASSIFICADO` permite medir a taxa de cobertura do classificador e melhorar
> patterns iterativamente sem corromper dados históricos.
>
> **Regra:** `NAO_CLASSIFICADO` **nunca altera fase**. Na `determinar_fase_analitica()`,
> eventos com este tipo são ignorados — a fase atual da proposição é mantida.

---

## O que fica para o R2

| Item | Motivo do adiamento |
|---|---|
| Tabela `materia_origem` | Correlação confiável Câmara↔Senado — complexidade alta para R1 |
| Tabela `medida_tempo` materializada | Otimização de performance — R1 calcula on-the-fly |
| Lógica preditiva (IA) | Depende de volume histórico acumulado pelo batch |

---

## Ordem de execução das etapas

```
Etapa 1 — branch + este documento                   ← você está aqui
Etapa 2 — entidades: FaseAnalitica, OrgaoLegislativo, EventoTramitacao
Etapa 3 — funções de domínio: classificar_tipo_evento(), determinar_fase_analitica()
Etapa 4 — NormalizarTramitacaoService + adapters
Etapa 5 — seed atualizado + endpoint GET /proposicoes/{id}/movimentacoes
Etapa 6 — cálculo de duração on-the-fly + DashboardService atualizado
```

Etapas 2a, 2b e 2c (as três entidades) podem ser desenvolvidas em paralelo.
Etapa 3 é gargalo: ninguém avança para 4 sem os testes das funções de domínio aprovados.

---

_Última atualização: ver histórico de commits._
