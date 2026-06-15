# Walkthrough Arquitetural: Implementação de Movimentações Analíticas (Issues #129, #130, #131)

Este documento descreve detalhadamente as decisões arquiteturais e a implementação passo a passo das funcionalidades analíticas de movimentações (R2), adotando a perspectiva de um Engenheiro de Software Sênior. O objetivo aqui não é apenas mostrar *o que* foi feito, mas o *porquê*, destacando os trade-offs e os padrões utilizados.

## 1. Contexto e Desafio

No Release 1 (R1), consolidamos a captura de dados brutos das APIs da Câmara e do Senado, armazenando-os como `EventoTramitacao`. No entanto, proposições históricas (ex: PL 4015/2023) geram centenas de eventos. Muitos são ruídos burocráticos (ex: "Publicação de Avulso", "Remessa à Coordenação").

**O Desafio:** Como apresentar uma timeline limpa e inteligível para o usuário final sem deletar dados brutos (que são cruciais para auditoria e rastreabilidade)?

**A Solução:** Adotar o padrão de **Event Sourcing** passivo na ingestão, mas criar visões materializadas (agregações) na camada de leitura. Dividimos o problema em três passos estritos:
1.  **Marcar** o que importa (Relevância).
2.  **Agrupar** o que é contínuo (Períodos de Fase).
3.  **Expor** de forma controlada (Query Param).

---

## Passo 1: O Domínio e a Regra de Relevância (Issue #129)

A primeira etapa foi definir o que torna um evento "relevante". Seguindo os princípios de *Domain-Driven Design* (DDD) definidos no `GEMINI.md`, regras de negócio devem pertencer à camada de Domínio, e não a Controllers ou Services genéricos.

### 1.1. A Entidade `EventoTramitacao`
No arquivo `src/domain/entities/evento_tramitacao.py`, centralizamos a lógica.

*   **Por que não usar um Service?** A relevância de um evento é uma característica intrínseca aos seus próprios dados (seu tipo, se mudou de fase, seu tempo de duração). Quando um objeto possui os dados necessários para tomar uma decisão sobre si mesmo, usamos o padrão *Information Expert*.
*   **Implementação:** Adicionamos a propriedade computada `@property eh_relevante`.

```python
# src/domain/entities/evento_tramitacao.py

TIPOS_SEMPRE_RELEVANTES = {
    TipoEvento.APRESENTACAO.value,
    # ... outros tipos
}

@property
def eh_relevante(self) -> bool:
    return (
        self.tipo_evento in TIPOS_SEMPRE_RELEVANTES
        or self.mudou_fase
        or self.deliberativo
        or (self.dias_na_etapa is not None and self.dias_na_etapa > 30)
        or self.marca_apensacao
    )
```

### 1.2. Trade-off de Persistência
Embora `eh_relevante` seja computável, decidimos **persistir** esse valor no banco de dados (`relevante: bool` no `EventoTramitacaoModel`).

*   **O Trade-off:** Duplicação de estado vs. Performance de Leitura.
*   **Decisão:** Em sistemas analíticos, leituras são muito mais frequentes que escritas (Read-Heavy). Se calculássemos on-the-fly, teríamos que buscar milhares de eventos no banco para o backend filtrá-los em memória (o infame problema N+1 disfarçado). Ao persistir, podemos delegar o filtro para o banco de dados (ex: `WHERE relevante = TRUE`), mantendo a API extremamente rápida. A atribuição ocorre no `NormalizarTramitacaoService`.

---

## Passo 2: O Agrupamento em Períodos (Issue #130)

Com os eventos marcados, precisávamos consolidar a timeline. Se uma lei passou 400 dias na "Análise de Comissões", gerando 20 eventos irrelevantes e 2 relevantes, a UI quer receber apenas 1 bloco: "Análise de Comissões (400 dias)".

### 2.1. O Value Object `PeriodoFase`
No DDD, um *Value Object* é um objeto sem identidade única, definido apenas pelos seus atributos. O agrupamento temporal é um cálculo gerado para leitura, logo, não possui um ID no banco de dados.

Criamos a `dataclass` `PeriodoFase` (`src/domain/value_objects/periodo_fase.py`). O uso de `dataclass` aqui é idiomático em Python para representar estruturas de dados imutáveis (ou puramente de transporte).

### 2.2. A Lógica de Agregação (`AgregarPorFaseService`)
No `src/application/services/agregar_por_fase_service.py`, criamos um serviço de domínio/aplicação puro (sem I/O de rede ou persistência, apenas transformação de dados).

O algoritmo é clássico processamento de stream:
1.  Ordena os eventos cronologicamente.
2.  Itera sobre a lista mantendo um ponteiro para a `fase_atual`.
3.  Quando a fase muda, "fecha" o período anterior (calculando os `dias_corridos`) e "abre" um novo.
4.  Eventos marcados como `relevante` (Passo 1) são acumulados dentro da lista `eventos_relevantes` do período ativo.

**Edge Case Importante:** O cálculo de dias do último evento aberto. Injetamos as flags `proposicao_encerrada` e `data_encerramento` para decidir se a data de saída é "hoje" (para projetos em andamento) ou a data final real do projeto. Isso garante precisão nas métricas do dashboard.

---

## Passo 3: Expondo a Solução (Issue #131)

Finalmente, conectamos a mecânica analítica à interface REST, garantindo retrocompatibilidade (para não quebrar integrações existentes).

### 3.1. Controller e Enums
Utilizamos o FastAPI para expor a feature via *Query Parameters*, mantendo a URL limpa.

Criamos o Enum `ModoMovimentacao` (`src/domain/value_objects/modo_movimentacao.py`) para garantir Type Safety e auto-documentação no Swagger/OpenAPI.

```python
# src/domain/value_objects/modo_movimentacao.py
class ModoMovimentacao(str, Enum):
    RESUMIDO = "resumido"
    COMPLETO = "completo"
    RELEVANTE = "relevante"
```

### 3.2. Orquestração no `ListarMovimentacoesService`
O `ListarMovimentacoesService` funciona como a fachada da camada de aplicação (Use Case). Ele delega a busca para o Repositório ou Adapters (se houver cache miss) e, por fim, aplica a estratégia de visualização.

```python
# Trecho do ListarMovimentacoesService
if modo == ModoMovimentacao.RESUMIDO:
    return self._agregar_service.executar(eventos, ...)

if modo == ModoMovimentacao.RELEVANTE:
    return [e for e in eventos if e.relevante]

return eventos # COMPLETO
```

### 3.3. DTOs (Data Transfer Objects)
No `proposicao_controller.py`, a rota agora retorna `Union[List[PeriodoFaseResponse], List[EventoTramitacaoResponse]]`. Adicionamos as funções `_to_evento_response` e `_to_periodo_response` para atuar como conversores (Mappers).

*   **Padrão Anti-Corrupção (ACL):** Esses mappers isolam a entidade de domínio do formato JSON retornado (ex: convertendo `snake_case` para `camelCase`).

---

## Resumo dos Padrões Aplicados

1.  **Information Expert (Domínio Puro):** `eh_relevante` residente na entidade, não em um Service.
2.  **Materialized View (Persistência da Relevância):** Gravar o resultado do cálculo analítico no banco para leitura rápida (Read-Heavy workload).
3.  **Value Objects (`PeriodoFase`):** Estruturas focadas em agregação e leitura temporal, sem identidade própria no banco.
4.  **Anti-Corruption Layer (Mappers no Controller):** Isolação rígida entre o Modelo (Entities) e a View (Pydantic Schemas/JSON).

Esta arquitetura garante que a lógica de "o que é importante no processo legislativo" esteja fortemente testada, isolada e reaproveitável, enquanto a API permanece rápida e flexível para os clientes de UI.

---

## Sugestões e Melhorias Futuras

Embora a implementação atual atenda aos requisitos do R2 e forneça uma base sólida para a análise de movimentações, o processo de desenvolvimento revelou oportunidades de refinamento e mitigação de dívida técnica.

### 1. Refatoração da Injeção de Dependências (Controllers)
Atualmente, os controllers instanciam repositórios e serviços diretamente:
```python
# proposicao_controller.py
evento_repo = SQLEventoTramitacaoRepository(session)
service = ListarMovimentacoesService(evento_repo, ...)
```
**Por que melhorar?** Isso acopla rigidamente a camada de apresentação às implementações específicas de infraestrutura, dificultando a injeção de *mocks* em testes de integração de nível mais alto e violando o Princípio de Inversão de Dependência (DIP).
**Solução Sugerida:** Utilizar o sistema de injeção de dependências do FastAPI (`Depends`) para resolver as instâncias de serviços e repositórios, permitindo que o controller dependa apenas de interfaces (Protocolos) e não de implementações concretas. *(Já mapeado na Issue #141).*

### 2. Delegação de Lógica de Consulta ao Repositório
No modo `RELEVANTE`, o filtro atualmente ocorre em memória na camada de serviço:
```python
if modo == ModoMovimentacao.RELEVANTE:
    return [e for e in eventos if e.relevante]
```
**Por que melhorar?** Embora eficiente para poucos eventos, se a carga aumentar ou se precisarmos de paginação, carregar tudo na memória para depois filtrar é ineficiente. Como já persistimos a flag `relevante` no banco, o banco de dados deve fazer esse trabalho.
**Solução Sugerida:** Expandir a interface do repositório para suportar filtros, como `evento_repo.buscar_por_proposicao(real_id, somente_relevantes=True)`. Isso reduzirá a carga de rede e uso de memória da aplicação.

### 3. Cache Distribuído (Redis) para a Agregação
O `AgregarPorFaseService` é eficiente, mas recalculá-lo a cada *hit* na API para proposições populares pode se tornar um gargalo.
**Por que melhorar?** Movimentações de leis antigas raramente mudam.
**Solução Sugerida:** Implementar uma camada de cache (ex: Redis) que armazene o payload JSON da agregação por fase (modo `resumido`), invalidando-o apenas quando um novo evento for detectado no processo de sincronização diária.

### 4. Machine Learning para Classificação de Eventos
A atual classificação de `TipoEvento` e a determinação de `eh_relevante` dependem de heurísticas baseadas em strings e regex (ex: buscar "Aprovado" na descrição).
**Por que melhorar?** A linguagem burocrática parlamentar varia muito e novas formas de descrever eventos são introduzidas constantemente, o que fatalmente resultará em eventos classificados incorretamente ou não classificados.
**Solução Sugerida:** Treinar e integrar um modelo NLP leve (ex: via uma fila assíncrona) que classifique as descrições brutas nos tipos definidos com base em inferência semântica, melhorando a precisão a longo prazo sem depender de regras rígidas no código.