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
