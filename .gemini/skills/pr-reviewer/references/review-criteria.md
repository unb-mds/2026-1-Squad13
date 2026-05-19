# Critérios de review para o projeto "Monitoramento de Tempo de Tramitação de Leis"

Este documento é referência para a skill `pr-reviewer` decidir quais pontos considerar sérios e quais são “nice‑to‑have”.

## Arquitetura (backend)

- Camada `presentation`:
  - Deve só rotear e validar input; NÃO deve conter regra de negócio.
- Camada `application`:
  - Deve conter Services/orquestradores; é o único ponto de coordenação de regras e integrações.
- Camada `domain`:
  - Deve ser puro; sem referência direta a HTTP, banco ou frameworks.
- Camada `infrastructure`:
  - Deve encapsular: banco, APIs externas (via Adapters) e cache.

## Adapter Pattern e Integração

- Toda integração com Câmara ou Senado deve ser feita via Adapters que implementam uma interface comum (Port).
- O domínio deve receber objetos normalizados (como `EventoTramitacao`), nunca o JSON bruto da API externa.
- Falhas de rede ou dados incompletos das APIs devem ser tratados com resiliência (ex.: try-except, valores default seguros).
