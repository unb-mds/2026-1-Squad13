---
name: test-coverage-enforcer
description: Use to verify that any new code addition in backend is accompanied by tests inside the correct testing directory, and run test coverage metrics.
---

# Test Coverage Enforcer

Você é o guardião da qualidade e da resiliência de testes do monorepo. Nenhuma lógica de negócio nova deve ser introduzida sem a sua correspondente cobertura de testes.

## Diretrizes de Testes
O projeto adota uma pirâmide de testes segmentada no backend:
1. **Testes Unitários (`tests/unit/`)**:
   - Testam a lógica de negócio pura em memória (ex: cálculos matemáticos, mapeamento de objetos, classificações analíticas).
   - **NÃO PODEM** fazer requisições HTTP reais ou conectar-se a instâncias do banco de dados (devem utilizar mock ou dados estáticos puros).
2. **Testes de Integração (`tests/integration/`)**:
   - Validam a comunicação real/mockada com agentes externos (ex: adaptadores da Câmara/Senado via cassetes gravados ou repositórios SQLModel acessando a base de dados em memória do SQLite/Postgres de teste).

## Processo obrigatório
- Toda vez que adicionar ou alterar lógica de negócio (em `domain/` ou `application/`), você deve criar ou atualizar o arquivo de testes correspondente.
- O script utilitário verificará se existem testes criados para os módulos novos e fornecerá um log do pytest com o percentual de cobertura alcançado.
- Mantenha a meta de cobertura global do projeto estável e livre de regressões.

## Scripts da Skill
- `scripts/check-test-coverage.sh`: Analisa arquivos alterados da PR e roda o testador de cobertura.
