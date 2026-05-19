# ADR-005: Padrão Adapter para isolamento das APIs externas

**Data:** 2026-04-09  
**Status:** Aceita  
**Decisores:** Arquiteto, Dev  

---

## Contexto

O sistema consome duas APIs com formatos diferentes:

- **Câmara:** chama proposições de "proposição", retorna JSON com campos como `id`, `ementa`, `dataUltimaAcao`, `statusProposicao.descricaoSituacao`
- **Senado:** chama proposições de "matéria", retorna JSON com estrutura diferente, campos com nomes distintos

Se o código que trata esses formatos estiver espalhado pelo sistema, qualquer mudança em uma das APIs vai exigir alterações em múltiplos lugares. Além disso, o domínio não deve conhecer detalhes de nenhuma API externa.

---

## Decisão

Vamos usar o **padrão Adapter** para isolar cada fonte de dados em um módulo dedicado na camada de Infraestrutura.

Cada adapter é responsável por:
1. Fazer as chamadas HTTP à API correspondente
2. Tratar paginação
3. Normalizar o formato da resposta para a entidade `Proposicao` do domínio

A camada de Aplicação trabalha apenas com a entidade `Proposicao` — nunca com o formato bruto das APIs.

```
CamaraAdapter  ──┐
                 ├──→ Proposicao (entidade do domínio)
SenadoAdapter  ──┘
```

Além da conversão de formatos, os Adapters e a camada de integração aplicarão duas regras de negócio cruciais:

**1. Deduplicação e Identificador Canônico:**
Proposições que tramitam em mais de uma casa (Câmara e Senado) representam a mesma proposição lógica no domínio do sistema. Para tratar isso, será criado um **identificador canônico** composto por `tipo + numero + ano` (ex: `PL_123_2023`). O sistema armazenará a origem do dado (Câmara ou Senado) e os IDs externos correspondentes (cross-reference) vinculados a este identificador único.

**2. Normalização de Status:**
O "caos" de diferentes status governamentais será mapeado para uma taxonomia interna padronizada e reduzida (Máquina de Estados). Os status normalizados iniciais serão: `EM_TRAMITACAO`, `APROVADA`, `REJEITADA`, `ARQUIVADA`, `PROMULGADA` e `DESCONHECIDA`. 
Para fins de auditoria e rastreabilidade (Data Lineage), o sistema persistirá:
*   O status original bruto (da API).
*   O status normalizado.
*   A origem da regra de mapeamento aplicada.

Implementação:

```python
# infrastructure/adapters/camara_adapter.py
class CamaraAdapter:
    def buscar_proposicoes(self, tema: str) -> list[Proposicao]:
        # chama API, pagina, normaliza → Proposicao
        ...

# infrastructure/adapters/senado_adapter.py
class SenadoAdapter:
    def buscar_materias(self, tema: str) -> list[Proposicao]:
        # chama API, pagina, normaliza → Proposicao
        ...
```

---

## Mapeamento de campos: Câmara → `Proposicao`

Endpoint principal: `GET /api/v2/proposicoes/{id}`  
Endpoint complementar: `GET /api/v2/proposicoes/{id}/autores`

| Campo da API Câmara | Campo em `Proposicao` | Observação |
|---|---|---|
| `dados.siglaTipo` | `tipo` | Ex: `"PL"`, `"PEC"` |
| `dados.numero` | `numero` | Convertido para `str` |
| `dados.ano` | `ano` | `int` |
| `dados.ementa` | `ementa` | Fallback: `"Sem ementa"` |
| `dados.dataApresentacao` | `data_apresentacao` | Formato `YYYY-MM-DDTHH:MM` |
| `statusProposicao.despacho` ou `statusProposicao.descricaoSituacao` | `status` | Prioridade: `despacho`; fallback: `"Sem status"` |
| `statusProposicao.dataHora` | `data_ultima_movimentacao` | |
| `statusProposicao.siglaOrgao` | `orgao_atual` | Fallback: `"N/A"` |
| `autores[0].nome` | `autor` | Fallback: `"Não informado"` |
| `autores[0].siglaUf` | `uf_autor` | Fallback: `"N/A"` |
| _(fixo)_ `"Câmara dos Deputados"` | `orgao_origem` | |
| _(gerado)_ URL da ficha de tramitação | `link_oficial` | `https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={id}` |

### Tramitações brutas: Câmara → dict intermediário

Endpoint: `GET /api/v2/proposicoes/{id}/tramitacoes`

| Campo da API Câmara | Campo no dict intermediário | Observação |
|---|---|---|
| `dataHora` | `data_hora` | |
| `sequencia` | `sequencia` | |
| `siglaOrgao` | `sigla_orgao` | Fallback: `"N/A"` |
| `descricaoTramitacao` + `" - "` + `despacho` | `descricao` | Concatenados quando distintos e não vazios |
| _(dict bruto completo)_ | `payload_bruto` | Preservado para auditoria (Data Lineage) |

---

## Mapeamento de campos: Senado → `Proposicao`

O Senado expõe dois endpoints com estruturas distintas. O adapter tenta o path A primeiro e cai no path B quando necessário.

### Path A — `DetalheMateria` (`GET /materia/{id}`)

| Campo da API Senado | Campo em `Proposicao` | Observação |
|---|---|---|
| `DetalheMateria.Materia.IdentificacaoMateria.DescricaoIdentificacaoMateria` | `tipo`, `numero`, `ano` | Parse de `"PL 123/2023"` |
| `DadosBasicosMateria.EmentaMateria` | `ementa` | Fallback: `"Sem ementa"` |
| `DadosBasicosMateria.DataApresentacao` | `data_apresentacao` | Formato `YYYY-MM-DD` |
| `DadosBasicosMateria.Autor` | `autor` | Fallback: `"Não informado"` |
| `SituacaoAtual.Autuacoes.Autuacao.Situacao.DescricaoSituacao` | `status` | Fallback: `"Sem status"` |
| `SituacaoAtual.Autuacoes.Autuacao.Situacao.DataSituacao` | `data_ultima_movimentacao` | Fallback: `data_apresentacao` |
| _(fixo)_ `"Senado Federal"` | `orgao_atual`, `orgao_origem` | |
| _(fixo)_ `"N/A"` | `uf_autor` | |
| _(gerado)_ URL da matéria | `link_oficial` | `https://wwws.senado.leg.br/ecidadania/visualizacaomateria?id={id}` |

### Path B — `Processo` (`GET /processo/{id}?v=1`, estrutura flat)

| Campo da API Senado | Campo em `Proposicao` | Observação |
|---|---|---|
| `identificacao` | `tipo`, `numero`, `ano` | Parse de `"PL 123/2023"` |
| `conteudo.ementa` ou `documento.ementa` | `ementa` | Fallback: `"Sem ementa"` |
| `documento.dataApresentacao` | `data_apresentacao` | |
| `autoriaIniciativa[0].autor` | `autor` | Fallback: `"Não informado"` |
| `autuacoes[0].situacoes[-1 com inicio].descricao` | `status` | Última situação com data preenchida |
| `autuacoes[0].situacoes[-1 com inicio].inicio` | `data_ultima_movimentacao` | Fallback: `data_apresentacao` |
| _(fixo)_ `"Senado Federal"` | `orgao_atual`, `orgao_origem` | |
| _(fixo)_ `"N/A"` | `uf_autor` | |
| _(gerado)_ URL da matéria | `link_oficial` | `https://wwws.senado.leg.br/ecidadania/visualizacaomateria?id={id}` |

### Tramitações brutas: Senado → dict intermediário

Endpoint: `GET /processo/{id_processo}?v=1`  
Nota: o adapter resolve `id_materia` → `id_processo` via `IdentificacaoProcesso` antes de consultar.

| Campo da API Senado | Campo no dict intermediário | Observação |
|---|---|---|
| `autuacoes[0].situacoes[].colegiado.sigla` | `sigla_orgao` | Fallback: `"Senado"` |
| `autuacoes[0].situacoes[].descricao` | `descricao` | |
| `autuacoes[0].situacoes[].inicio` | `data_hora` | |
| _(contador incremental)_ | `sequencia` | A API retorna da mais recente para a mais antiga; o adapter inverte antes de numerar |
| _(dict bruto do item situação)_ | `payload_bruto` | Preservado para auditoria (Data Lineage) |

---

## Mapeamento de campos: Entidades do domínio → DTOs da API

### `Proposicao` → `ProposicaoResponse` (snake_case → camelCase)

Realizado em `_to_response()` no `proposicao_controller.py`.

| Campo em `Proposicao` | Campo JSON retornado | Tipo | Observação |
|---|---|---|---|
| `id` | `id` | `str` | |
| `tipo` | `tipo` | `str` | |
| `numero` | `numero` | `str` | |
| `ano` | `ano` | `int` | |
| `ementa` | `ementa` | `str` | |
| `ementa_resumida` | `ementaResumida` | `str?` | |
| `autor` | `autor` | `str` | |
| `orgao_origem` | `orgaoOrigem` | `str?` | |
| `status` | `status` | `str` | Já normalizado por `normalizar_campo_status()` |
| `orgao_atual` | `orgaoAtual` | `str` | |
| `data_apresentacao` | `dataApresentacao` | `str` | |
| `data_ultima_movimentacao` | `dataUltimaMovimentacao` | `str` | |
| `tempo_total_dias` | `tempoTotalDias` | `int` | Fallback: `0` |
| `tem_atraso` | `temAtraso` | `bool` | Fallback: `false` |
| `atraso_critico` _(property)_ | `atrasoCritico` | `bool` | `tempo_total_dias > 180` |
| `tem_previsao_ia` | `temPrevisaoIA` | `bool` | Fallback: `false` |
| `tags` | `tags` | `str[]` | Fallback: `[]` |
| `link_oficial` | `linkOficial` | `str?` | |
| `codigo_normalizado` _(property)_ | `codigoNormalizado` | `str?` | Ex: `"PL-123-2024"` |
| `data_encerramento` | `dataEncerramento` | `str?` | |
| `previsao_aprovacao_dias` | `previsaoAprovacaoDias` | `int?` | |

### `EventoTramitacao` → `EventoTramitacaoResponse` (snake_case → camelCase)

Realizado em `_to_evento_response()` no `proposicao_controller.py`.  
Endpoint: `GET /proposicoes/{id}/movimentacoes`

| Campo em `EventoTramitacao` | Campo JSON retornado | Tipo | Observação |
|---|---|---|---|
| `proposicao_id` | `proposicaoId` | `str` | |
| `data_evento` | `dataEvento` | `str` | Espaço substituído por `T`; sufixo `Z` adicionado se ausente |
| `sequencia` | `sequencia` | `int` | |
| `sigla_orgao` | `siglaOrgao` | `str?` | |
| `descricao_original` | `descricaoOriginal` | `str` | |
| `tipo_evento` | `tipoEvento` | `str` | Valor do enum `TipoEvento` (ex: `"VOTACAO_PLENARIO"`) |
| `fase_analitica_id` | `faseAnaliticaId` | `int?` | |
| `deliberativo` | `deliberativo` | `bool` | |
| `mudou_fase` | `mudouFase` | `bool` | |
| `mudou_orgao` | `mudouOrgao` | `bool` | |
| `remessa_ou_retorno` | `remessaOuRetorno` | `str?` | `null`, `"REMESSA"` ou `"RETORNO"` |

---

## Taxonomia de status normalizado (implementação real)

A ADR originalmente propôs um enum uppercase (`EM_TRAMITACAO`, `APROVADA`, etc.). A implementação real em `Proposicao.normalizar_campo_status()` adota strings human-readable para exibição direta na interface:

| Condição (status bruto contém) | Valor normalizado |
|---|---|
| `"NORMA JURÍDICA"` | `"Concluída (Lei)"` |
| `"SANCIONAD"` | `"Sancionada"` |
| `"VETAD"` | `"Vetada"` |
| `"REJEITAD"`, `"ARQUIVAD"`, `"PREJUDICAD"`, `"RETIRAD"` | `"Arquivada"` |
| `"APROVAD"` | `"Aprovada"` |
| `"PAUTA"` | `"Em Pauta"` |
| `"RELATOR"` | `"Em Relatoria"` |
| `"AGUARDANDO"` | `"Aguardando"` |
| `"RECEBIMENTO"`, `"ENCAMINHAD"`, `"DESPACHO"`, `"DISTRIBUIÇÃO"` | `"Em Tramitação"` |
| Sem status ou `"sem status"` | `"Em Tramitação"` |
| Nenhum padrão acima + texto > 50 chars | Truncado em 47 chars + `"..."` |

O frontend (`shared/types/index.ts`) define `StatusProposicao` com um conjunto diferente de valores literais. Há divergência intencional: o domínio é mais granular que o tipo TypeScript declarado.

---

## Depreciação de `Tramitacao`

A entidade `Tramitacao` (campos: `data_hora`, `descricao_tramitacao`, `despacho`, `status`) foi substituída por `EventoTramitacao` como modelo analítico persistido. O mapeamento de depreciação está documentado no cabeçalho de `evento_tramitacao.py`:

| Campo antigo (`Tramitacao`) | Campo novo (`EventoTramitacao`) |
|---|---|
| `id` | `evento_id` |
| `proposicao_id` | `proposicao_id` (FK mantida) |
| `data_hora` | `data_evento` |
| `sequencia` | `sequencia` |
| `sigla_orgao` | `sigla_orgao` |
| `descricao_tramitacao` + `despacho` | `descricao_original` (consolidado) |
| `status` | _(removido; substituído por `tipo_evento`)_ |
| _(ausente)_ | `tipo_evento`, `fase_analitica_id`, `deliberativo`, `mudou_fase`, `mudou_orgao`, `remessa_ou_retorno`, `payload_bruto` |

`Tramitacao` subsiste temporariamente como DTO interno no pipeline de coleta, sem tabela no banco.

---

## Gap conhecido: dessincronia no consumo de movimentações pelo frontend

O método `obterMovimentacoes` em `frontend/src/shared/lib/api.ts` lê `dataHora` e `descricaoTramitacao` do payload retornado, mas o backend retorna `dataEvento` e `descricaoOriginal`. Isso faz com que os campos `data` e `descricao` de `MovimentacaoTramitacao` sempre caiam nos valores de fallback (`new Date().toISOString()` e `"Tramitação registrada"`). Correção pendente em issue separada — não alterar este adapter para contornar.

---

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| Adapter por fonte (escolhida) | Mudança na API afeta só o adapter; domínio isolado | Dois arquivos para manter |
| Chamada direta nos services | Menos arquivos | Services acumulam lógica de HTTP + normalização |
| Client genérico único | Um só lugar para HTTP | Normalização vira um if/else gigante por fonte |

---

## Consequências

**Positivas:**
- Se a Câmara mudar o formato de resposta, só `CamaraAdapter` muda
- Se o Senado exigir autenticação no futuro, só `SenadoAdapter` muda
- A camada de Aplicação e o Domínio não precisam saber que existem duas fontes
- Fácil de adicionar uma terceira fonte (ex: API de comissões) sem tocar no restante

**Negativas / trade-offs:**
- Mais arquivos do que uma implementação direta
- Time precisa entender o padrão para não "vazar" lógica da API para os services

**Riscos:**
- Normalização incompleta pode introduzir campos `None` que quebram o domínio
- Mitigação: validação com Pydantic na saída de cada adapter antes de retornar `Proposicao`
