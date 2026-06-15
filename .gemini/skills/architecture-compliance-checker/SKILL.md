---
name: architecture-compliance-checker
description: Use to check if the layered architectural limits are respected, verifying that code in domain has zero dependencies on other layers, and application does not import presentation.
---

# Architecture Compliance Checker

Você é responsável por blindar os limites de acoplamento entre as camadas do projeto. A conformidade arquitetural garante a manutenibilidade e a testabilidade de longo prazo do monorepo.

## Diretrizes das Camadas do Backend
O projeto adota **Layered Architecture**. As importações de código são permitidas apenas na direção descendente:

```mermaid
graph TD
    P[presentation: FastAPI / Rotas] --> A[application: Services / Casos de Uso]
    A --> D[domain: Entities / Regras de Negócio]
    P --> D
    I[infrastructure: DB / Adapters / Cache] --> D
    A --> I
```

### Regras Estritas de Importação:
1. **domain (Núcleo Puro)**:
   - **NÃO PODE** importar nada das camadas `infrastructure`, `application` ou `presentation`.
   - Deve conter apenas Python puro, tipos e decorações de dados permitidas (como SQLModel, conforme ADR-001).
2. **application (Casos de Uso)**:
   - **NÃO PODE** importar nada da camada `presentation`.
   - Pode importar do `domain` e interfaces/ports ou models básicos de `infrastructure`.
3. **presentation (Interface HTTP)**:
   - Pode importar de `application` e `domain`.
   - **NÃO PODE** conter regras de negócio complexas (deve apenas rotear e validar tipos de requisição).

## Processo obrigatório
- Antes de submeter uma PR ou considerar um desenvolvimento como concluído, execute o validador local de camadas.
- O script utilitário analisará a árvore sintática abstrata (AST) dos arquivos Python criados ou modificados, verificando violações de imports ilegais de forma rápida e estática.
- Corrija qualquer importação ilegal removendo o acoplamento ou aplicando o padrão de injeção de dependência / Ports & Adapters.

## Scripts da Skill
- `scripts/verify-layers.sh`: Identifica arquivos alterados no monorepo e chama o script de checagem.
- `scripts/check-imports.py`: Validador sintático Python que aponta imports ilegais por arquivo.
