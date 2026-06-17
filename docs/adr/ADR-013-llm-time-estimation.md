# ADR: Implementação do MVP de Estimativa de Tempo via LLM (Gemini 1.5 Flash)

**Status:** Proposto / Aceito  
**Data:** 17 de Junho de 2026  
**Contexto:** LexTrack (Monitoramento de Tempo de Tramitação de Leis)

## 1. Contexto e Motivação
O projeto LexTrack tem como objetivo fornecer uma estimativa preditiva do tempo de tramitação de proposições legislativas. Devido a restrições estritas de tempo para a release atual (MVP) e ausência de orçamento para infraestrutura de nuvem, abordagens tradicionais e modelos proprietários pagos precisaram ser reavaliados para este primeiro ciclo de desenvolvimento.

A solução adotada utiliza o modelo Gemini 1.5 Flash por meio da API gratuita do Google AI Studio. Esta abordagem ("Via Expressa") permite a validação imediata do fluxo de dados de ponta a ponta, transferindo a complexidade analítica para um modelo fundacional já treinado com vasto conhecimento do ordenamento jurídico e do processo legislativo brasileiro.

## 2. Decisão e Alternativas Consideradas

**Decisão:** Optou-se pela utilização da API gratuita do Gemini 1.5 Flash.

**Alternativas Descartadas:**
* **Modelos de Machine Learning Clássicos (Regressão/Classificação):** Descartados para o MVP devido à necessidade de estruturação de um *pipeline* completo de engenharia de dados (*features*), treinamento, *deploy* e custos de infraestrutura de computação para servir o modelo.
* **Modelos Open-Source Locais (ex: Llama 3 via Ollama):** Descartados por exigirem hardware dedicado (GPUs de alto desempenho) para execução em ambiente de *staging*/*produção*, inviabilizando o requisito de custo zero de infraestrutura no momento atual.
* **LLMs Pagos (ex: GPT-4o, Claude 3.5 Sonnet):** Descartados devido ao orçamento nulo alocado para o projeto nesta fase inicial.

## 3. Consequências

### Consequências Positivas:
* **Velocidade de Entrega:** Entrega imediata da funcionalidade preditiva sem necessidade de treinamento de modelos do zero.
* **Custo Zero:** Alinhamento estrito com as restrições orçamentárias do MVP.
* **Capacidade Semântica:** Excelente compreensão de textos jurídicos complexos (ementas de projetos de lei) nativa do modelo.

### Consequências Negativas / Riscos:
* **Vendor Lock-in Temporário:** Acoplamento inicial à especificação da API do Google (risco mitigado pelo desenho arquitetural hexagonal).
* **Latência de Rede:** Dependência de chamadas HTTP externas, o que pode impactar o tempo de resposta da requisição se comparado a uma solução local ou em cache.
* **Limitações do Free Tier:** Sujeição a limites estritos de requisições (*rate limit* de 15 RPM) e instabilidades do serviço gratuito.

## 4. Requisitos do Sistema

### Requisitos Funcionais (RF)
* **RF01:** O sistema deve receber os metadados de uma proposição (ementa, tema, número de emendas, assinaturas, autor, etc.).
* **RF02:** O sistema deve construir dinamicamente um *prompt* estruturado contendo os dados da proposição e as instruções de inferência.
* **RF03:** O sistema deve realizar uma chamada assíncrona à API do Gemini 1.5 Flash.
* **RF04:** O sistema deve retornar um objeto JSON padronizado contendo o tempo estimado (em dias), um índice de confiança da IA e uma justificativa textual curta.
* **RF05 (Observabilidade):** O sistema deve persistir a estimativa gerada no banco de dados vinculada à proposição, permitindo que, no futuro, seja comparado o `tempo_estimado` com o `tempo_real` (quando a tramitação for concluída) para fins de auditoria e *fine-tuning*.
* **RF06 (Apresentação e Transparência):** Toda estimativa gerada por inteligência artificial deve ser exibida na interface do usuário (frontend) acompanhada de um aviso explícito (*disclaimer*) informando que se trata de uma análise preditiva estatística computacional, não configurando um prazo legal garantido.

### Requisitos Não Funcionais (RNF)
* **RNF01 (Arquitetura):** A implementação deve respeitar rigorosamente a separação de responsabilidades (*Ports and Adapters*), blindando a camada de Domínio de qualquer dependência direta da SDK do Google.
* **RNF02 (Custo):** O custo de inferência deve ser zero, utilizando estritamente o *Free Tier* da API do Google AI Studio.
* **RNF03 (Resiliência e Robustez):** O adaptador deve implementar tratamento de erros para indisponibilidades temporárias e *Rate Limiting* da API. Deve utilizar a biblioteca Pydantic para validar a integridade do JSON retornado.
* **RNF04 (Fallback):** Caso o modelo falhe ou retorne uma estrutura inválida repetidas vezes, o sistema deve acionar uma estratégia de contingência (*Fallback Strategy*), retornando uma média histórica padronizada ou um erro tratado, impedindo a quebra da aplicação.

## 5. Desenho Arquitetural
A arquitetura segue o padrão de Arquitetura Hexagonal (*Ports and Adapters*) para garantir que o núcleo de negócio seja agnóstico à tecnologia de IA escolhida.
[Image of Hexagonal Architecture pattern diagram]

### 5.1. Camada de Domínio (`domain/`)
O domínio é isolado e define apenas os contratos de entrada e saída.
* **Porta (Interface):** Criação da interface `IAEstimativaPort` definindo o contrato de inferência.
* **DTOs:** Modelos de dados de entrada (`ProposicaoEstimativaRequest`) e de saída (`EstimativaResponse`, contendo `dias_estimados`, `confianca` e `justificativa`).
* **Serviço:** O `EstimativaService` orquestra o fluxo de negócio invocando os métodos definidos na Porta.

### 5.2. Camada de Infraestrutura (`infrastructure/`)
Contém as implementações técnicas e acoplamentos com serviços externos.
* **Adaptador:** Criação do `GeminiLLMAdapter` em `infrastructure/adapters/gemini_llm_adapter.py`.
* **Responsabilidade:** Implementar a interface `IAEstimativaPort`. Esta classe recebe o DTO do domínio, renderiza o *prompt*, gerencia as credenciais (via `.env`), realiza a chamada assíncrona HTTP, valida a estrutura da resposta (Pydantic) e trata cenários de erro antes de devolver o DTO populado.
* **Mecanismo de Otimização de Cota (Cache):** Para mitigar o limite estrito de requisições por minuto do plano gratuito, uma camada de cache (Redis) interceptará as requisições. Consultas para a mesma proposição (mesmos metadados e ID) recuperarão o valor armazenado em cache, evitando chamadas redundantes e preservando a cota da API.

## 6. Estratégia de Prompt Engineering (System Instruction)
O adaptador enviará uma instrução de sistema rigorosa utilizando a técnica de *Chain of Thought* (Cadeia de Pensamento) para forçar o modelo a processar os dados antes de responder, mitigando alucinações e garantindo saídas determinísticas:

```text
Você é um consultor legislativo sênior do Congresso Nacional Brasileiro.
Analise os metadados da proposição fornecida (autor, tema, ementa, regime de tramitação).

Siga os seguintes passos mentalmente antes de responder:
1. Identifique a complexidade do tema e o rito de tramitação provável.
2. Lembre-se de gargalos comuns (comissões, vista, emendas) associados a esse tipo de proposição.
3. Estime o tempo total de tramitação em dias baseado em proposições similares.

Após a análise, retorne APENAS um JSON válido e estrito no seguinte formato:
{
  "dias_estimados": int,
  "confianca": float, // Valor de 0.0 a 1.0 indicando sua certeza na estimativa
  "justificativa": "string" // Explicação sucinta de até 2 frases
}

CRÍTICO: Não inclua NENHUMA formatação markdown (como ```json) ou qualquer texto complementar fora do objeto JSON. A saída deve ser exclusivamente o JSON em texto puro.
```

## 7. Plano de Implementação e Commits Atômicos
Para garantir a rastreabilidade e a integridade da *branch* `develop`, o desenvolvimento será fatiado nas seguintes etapas:

* `feat: cria DTOs e IAEstimativaPort na camada de dominio` (Definição exclusiva de contratos, interfaces e estruturas de dados de negócio, sem dependências externas).
* `feat: implementa GeminiLLMAdapter com validacao Pydantic e estrategia de fallback` (Configuração da SDK/HTTP cliente, lógica de construção do *prompt*, validação de esquema com Pydantic e tratamento de exceções de rede/rate limit).
* `feat: adiciona camada de cache Redis para estimativas de proposicoes` (Implementação do mecanismo de interceptação e armazenamento de requisições idênticas para proteção da cota da API).
* `test: adiciona testes unitarios e mocks para o adaptador LLM e cache` (Garantia de cobertura de testes simulando falhas de rede, respostas inválidas da IA e acionamento correto do comportamento de fallback).
* `chore: atualiza injecao de dependencias para vincular o port ao adapter` (Configuração do container de injeção de dependências da aplicação para realizar o *binding* final entre a interface e a infraestrutura).
