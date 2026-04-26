# ADR-005: Padrão Adapter para isolamento das APIs externas

**Data:** 2026-04-09  
**Status:** Proposta  
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
3. Normalizar o formato da resposta para a entidade `Lei` do domínio

A camada de Aplicação trabalha apenas com a entidade `Lei` — nunca com o formato bruto das APIs.

```
CamaraAdapter  ──┐
                 ├──→ Lei (entidade do domínio)
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
    def buscar_proposicoes(self, tema: str) -> list[Lei]:
        # chama API, pagina, normaliza → Lei
        ...

# infrastructure/adapters/senado_adapter.py
class SenadoAdapter:
    def buscar_materias(self, tema: str) -> list[Lei]:
        # chama API, pagina, normaliza → Lei
        ...
```

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
- Mitigação: validação com Pydantic na saída de cada adapter antes de retornar `Lei`
