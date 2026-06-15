# ADR-010: Separação de status e status_original em Proposições

**Data:** 2026-06-08  
**Status:** Aceita  
**Decisores:** Caio Martins (Arquiteto de Domínio/Analista Técnico) e Gemini

---

## Contexto

Atualmente, o sistema apresenta inconsistências, acoplamento e redundância na representação de status de proposições legislativas (PL/PEC). A coluna `status` no modelo `ProposicaoModel` possui sobrecarga de responsabilidades:
1. Funciona como cache bruto de strings livres retornadas pelas APIs externas da Câmara e do Senado (ex: `"Aguardando Parecer do Relator na CCJC"`).
2. É usada como campo de busca exata em filtros no painel de listagem e nas agregações do dashboard analítico.

Como consequência:
* Filtros por status falham silenciosamente para a grande maioria das proposições recém-coletadas (pois o banco possui o texto bruto, enquanto o frontend envia termos normalizados como `"Em Tramitação"`).
* O dashboard de métricas depende de cláusulas `CASE WHEN` com buscas `ILIKE` complexas em tempo de execução para agrupar as strings livres, gerando duplicação de regras de negócio em relação ao domínio (`Proposicao.normalizar_campo_status`) e risco constante de divergências analíticas.

## Decisão

Adotamos a separação do campo de status em dois níveis de representação tanto no domínio quanto no banco de dados persistido:

1. **`status`**: Valor canônico, limpo e normalizado do domínio (ex: `"Em Tramitação"`, `"Em Pauta"`, `"Arquivada"`). Este campo será a **única fonte de verdade** para filtros, contagens, ordenações, agregações e gráficos no dashboard.
2. **`status_original`**: Texto bruto, rico e explicativo retornado originalmente pelas APIs da Câmara e do Senado (ex: `"Aguardando Parecer do Relator..."`). Este campo será preservado estritamente para o detalhe individual da proposição, timelines de eventos e rastreabilidade metodológica.

Adicionalmente:
* A normalização de status será executada na entrada de dados e antes da persistência, tanto na coleta em lote (`ColetarEmLoteService`) quanto nas consultas individuais (`DetalheProposicaoService`).
* As regras de agrupamento do dashboard analítico serão simplificadas no repositório SQL para operar apenas sobre a lista fechada dos 10 status normalizados pelo domínio:
  * **Em tramitação** = `Em Tramitação`, `Em Relatoria`, `Em Pauta`, `Aguardando`
  * **Aprovada/Sancionada** = `Aprovada`, `Sancionada`, `Concluída (Lei)`
  * **Rejeitada/Arquivada** = `Arquivada`, `Arquivada (Apensada)`, `Vetada`

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **1. Separar campos (Duas colunas)** | Preserva o andamento exato (rastreabilidade) no detalhe; permite buscas exatas indexadas e limpas por status normalizado; elimina o acoplamento do repositório a strings brutas. | Requer migração de banco e alteração de schema. |
| **2. Normalizar apenas no retorno da API** | Sem mudanças no schema do banco. | Filtros de busca e agregados continuam dependendo de buscas textuais `ILIKE` ineficientes e duplicação crítica de regras em SQL. |
| **3. Manter apenas status normalizado (Sobrescrever)** | Simples implementação; sem nova coluna. | Perda definitiva de nuance jurídica e despachos específicos no detalhe da proposição. |

## Consequências

**Positivas:**
* **Consistência Semântica**: O mesmo status exibido na listagem, filtros e dashboard agora compartilha da mesma regra do domínio.
* **Corretude nos Filtros**: Consultas por status no frontend (ex: `"Em Tramitação"`) passam a funcionar imediatamente por igualdade exata na coluna indexada do banco.
* **Performance e Simplicidade no SQL**: Remoção de cláusulas `CASE WHEN ILIKE` pesadas e complexas no repositório do dashboard. O agrupamento passa a mapear uma lista restrita e conhecida de termos.
* **Preservação de Detalhes**: O usuário continua visualizando o andamento real e descritivo da proposição na página de detalhe.

**Negativas / trade-offs:**
* Necessidade de alteração do schema de persistência (`ProposicaoModel`) e das entidades de domínio para acomodar o novo atributo `status_original`.
* Processamento extra na gravação (a normalização é executada ativamente na coleta em lote).
* Perda de nuance transitória no nível agregado do dashboard (ex: não é possível ver quantas matérias estão "Em Pauta" na dashboard principal, apenas que estão "Em tramitação"). Esse trade-off é aceitável, pois essa nuance operacional pode ser obtida por filtros na listagem ou na página de detalhes.
