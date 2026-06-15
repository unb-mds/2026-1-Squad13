# Documento Técnico: Correção de Identidade Canônica, Histórico Legislativo e Cache do Dashboard

## 🎯 Objetivo

Este documento consolida a especificação arquitetural para a correção do fluxo de Ingestão e Cache do LexTrack. O objetivo é solucionar as colisões de chaves canônicas de proposições em diferentes regimes de tramitação, preservar metadados históricos de autoria e origem (casa iniciadora) e garantir a consistência e sincronização de dados exibidos no frontend por meio da invalidação ativa de cache no Redis.

---

## ⚠️ Problema Identificado

O fluxo de ingestão atual do LexTrack trata proposições de diferentes casas e épocas sob uma chave de identificação canônica comum `(tipo, numero, ano)`. Isso gera três impactos indesejados no banco de dados e no frontend:

1.  **Sobrescrita Destrutiva de Metadados**: A importação dos dados do Senado de uma matéria bicameral sobrescreve dados de autoria e de origem cadastrados pela Câmara dos Deputados (ou vice-versa), apagando a rastreabilidade da casa iniciadora.
2.  **Perda de Rastreabilidade e Colisão em Regimes Antigos**:
    *   Proposições independentes anteriores a 2019 de casas diferentes com a mesma numeração (ex: `PL 100/2015 da Câmara` e `PL 100/2015 do Senado`) sofrem colisão direta de chave canônica e se sobrescrevem, resultando em perda de registros no banco.
    *   Matérias antigas que transitaram de casa mudando de identificação (ex: `PL 1234/2015` virando `PLC 56/2016` no Senado) entram como entidades separadas sem correlação a nível de registro de proposição.
3.  **Latência e Desatualização no Dashboard**: O cache de 24 horas no Redis (`cache_ttl = 86400`) para consultas gerais do dashboard faz com que os dados exibidos no frontend fiquem desatualizados, mesmo após ingestões bem-sucedidas no PostgreSQL.

---

## 🔍 Diagnóstico Funcional

### 1. Identidade da Proposição (Ato Conjunto nº 1/2018)
A partir de **2 de fevereiro de 2019**, as matérias bicaminais passaram a adotar uma **identificação unificada** no Congresso Nacional.
*   Uma matéria bicameral pós-2019 corresponde a uma **entidade canônica única** no banco de dados.
*   No entanto, a **casa de origem (iniciadora)** e o **autor original** não podem ser perdidos ou sobrescritos pela casa revisora.
*   As movimentações entre as casas devem ser registradas como eventos no histórico de tramitação, e não através da sobrescrita de atributos de cabeçalho da proposição.

### 2. Histórico Legislativo e Transição de Matérias
Matérias anteriores a 2019 mantiveram a numeração antiga e independente de cada Casa. Elas só passaram a adotar o regime de identificação unificada caso tenham transitado (migrado) de casa a partir de fevereiro de 2019.
*   **Proposições independentes sem trânsito**: Devem coexistir como registros separados. A chave primária deve impedir a colisão destas.
*   **Proposições antigas que transitaram pré-2019 (com números diferentes)**: Devem manter registros de proposição separados no banco para preservar os dados de cada casa histórica, mas estarem ligadas por uma tabela de correlação de histórico legislativo.

### 3. Sincronização de Cache do Dashboard
O frontend deve refletir em tempo real (ou com latência mínima) o sucesso de novas rodadas dos workers. O cache do Redis deve ser gerenciado de forma **ativa**, utilizando invalidação por eventos de escrita em vez de depender apenas do TTL de 24 horas.

---

## 📐 Proposta de Modelagem Técnica

### A. Estrutura da Entidade e Contexto

A identidade primária da proposição em domínio e banco deve ser mantida estável. No entanto, para diferenciar proposições monocamerais independentes de anos passados e preservar metadados, a tabela `proposicao` (`ProposicaoModel` em [proposicao_model.py](file:///home/caio/2026-1-Squad13/backend/src/infrastructure/database/models/proposicao_model.py)) e a entidade `Proposicao` ([proposicao.py](file:///home/caio/2026-1-Squad13/backend/src/domain/entities/proposicao.py)) receberão ou garantirão a persistência dos seguintes campos de controle:

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `orgao_origem` (casa_origem) | `VARCHAR` | Identifica a Casa Legislativa iniciadora (Câmara ou Senado). Permanece imutável após a inserção. |
| `orgao_atual` (casa_atual) | `VARCHAR` | Identifica onde a matéria se encontra tramitando no momento (Câmara, Senado ou Executivo). |
| `numero_original_casa` | `VARCHAR` | Armazena o número do projeto na casa onde ele iniciou (importante para transições pré-2019). |
| `sigla_original` | `VARCHAR` | Sigla da proposição na casa de origem. |
| `status_original` | `VARCHAR` | O status bruto retornado pela API daquela casa legislativa. |
| `data_primeira_coleta` | `TIMESTAMP` | Data e hora em que a proposição foi inserida no banco do LexTrack pela primeira vez. |
| `data_ultima_atualizacao` | `TIMESTAMP` | Data e hora do último reprocessamento ou atualização física do registro. |

### B. Tabelas de Correlação e Histórico Legislativo

Para rastrear a cadeia de trâmite de proposições que mudaram de identificação e sigla (Regime 2), serão utilizadas duas tabelas estruturadas na camada de infraestrutura:

#### 1. Tabela de Correlação de Proposições (`proposicao_correlacao`)
Esta tabela registra o vínculo entre registros de proposições separados no banco que representam a mesma matéria histórica:
```sql
CREATE TABLE proposicao_correlacao (
    correlacao_id SERIAL PRIMARY KEY,
    proposicao_origem_id VARCHAR NOT NULL REFERENCES proposicao(id),
    proposicao_destino_id VARCHAR NOT NULL REFERENCES proposicao(id),
    tipo_vinculo VARCHAR NOT NULL, -- 'unificacao_post_2019', 'revisao_pre_2019', 'apensamento'
    data_associacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. Tabela de Eventos de Tramitação (`evento_tramitacao`)
Garantir que todas as transições de casa de um projeto bicameral unificado (Regime 3) sejam inseridas como linhas históricas nesta tabela (com código de fase correspondente, ex: `REMESSA_OUTRA_CASA` ou `RECEBIMENTO_OUTRA_CASA`), em vez de alterar os cabeçalhos originais do projeto.

---

## 🛠️ Ajustes no Processo de Upsert (`SQLProposicaoRepository`)

O método `upsert_em_lote_por_numero_canonico` em [sql_proposicao_repository.py](file:///home/caio/2026-1-Squad13/backend/src/infrastructure/repositories/sql_proposicao_repository.py#L39) passará a operar com uma **lógica de mesclagem inteligente e condicional**:

1.  **Diferenciação por Regime de Ano**:
    *   **Ano de Ingestão < 2019 ou Tipo Monocamerais**: A chave de correspondência para determinar a existência do registro será expandida para incluir a origem: `(tipo, numero, ano, orgao_origem)`. Isso isola e previne a colisão física de registros independentes da Câmara e do Senado.
    *   **Ano de Ingestão >= 2019 e Tipo Bicameral**: A chave canônica de busca e associação continua sendo `(tipo, numero, ano)`, garantindo a representação de registro único bicameral.
2.  **Mesclagem Não-Destrutiva**:
    *   Ao encontrar uma proposição unificada existente no banco, a mesclagem deve excluir da atualização os campos imutáveis de origem caso eles já estejam populados:
        ```python
        campos_preservar = {"id", "tipo", "numero", "ano", "orgao_origem", "autor", "data_apresentacao", "data_primeira_coleta"}
        ```
    *   Apenas dados mutáveis de estado atual (ex: `orgao_atual`, `status`, `data_ultima_movimentacao`, `tempo_total_dias`, `tags`) serão atualizados no banco de dados.

---

## ⚡ Ajustes na Sincronização de Cache do Dashboard

Para que as consultas de dashboard respondam dinamicamente e sem atraso a novas rodadas dos workers, o backend adotará a estratégia de **Invalidação Ativa de Cache (Write-Through/Invalidate-on-Write)**:

1.  **Helper de Invalidação no Redis**:
    Será implementado um método no `RedisClient` para deletar chaves que combinem com um padrão glob (ex: `dashboard:*`).
2.  **Invalidação após Escrita**:
    Nas funções dos workers do Celery (em [coleta_worker.py](file:///home/caio/2026-1-Squad13/backend/src/infrastructure/workers/coleta_worker.py)), imediatamente após um lote de proposições ser inserido/atualizado com sucesso no banco, o worker executará a limpeza das chaves de dashboard no Redis.
3.  **Fallback por TTL**:
    O TTL das chaves de dashboard continuará configurado como mecanismo de proteção secundário de memória, reduzido de 24 horas para **1 hora** para evitar obsolescência crônica caso ocorram falhas na invalidação direta.

---

## 🧪 Estratégia de Testes e Validação

A validação das correções abrangerá testes de unidade e integração:

1.  **Isolamento Pré-2019**:
    *   *Cenário*: Tenta persistir o `PL 100/2015` com `orgao_origem = "Câmara dos Deputados"` e o `PL 100/2015` com `orgao_origem = "Senado Federal"`.
    *   *Resultado Esperado*: O banco de dados deve registrar **2 linhas distintas** no final da execução, com IDs e dados preservados de forma isolada.
2.  **Mesclagem Pós-2019**:
    *   *Cenário*: Salva o `PL 50/2020` da Câmara (autor: Deputado X, orgao: Câmara) e depois roda a coleta do mesmo `PL 50/2020` no Senado (autor: Senador Y, orgao: Senado).
    *   *Resultado Esperado*: O banco deve manter **1 linha** com `id = "camara:50"`, mas com `orgao_origem = "Câmara dos Deputados"` e `autor = "Deputado X"` preservados. O `orgao_atual` deve refletir `"Senado Federal"`.
3.  **Invalidação do Cache**:
    *   *Cenário*: Consulta as métricas do dashboard, executa o worker inserindo uma nova proposição limpa e consulta as métricas novamente.
    *   *Resultado Esperado*: A contagem de proposições retornada na segunda chamada deve refletir imediatamente o aumento no PostgreSQL, comprovando que o Redis foi limpo de forma ativa.
