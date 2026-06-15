# Regras de Backlog e Priorização

Orientações para transformar achados de auditoria em tarefas acionáveis.

## 1. Granularidade
- Evite issues gigantes ("Refatorar Dashboard").
- Prefira tarefas granulares ("Corrigir tokens de cor no KPICard do Dashboard").

## 2. Priorização (Matriz de Impacto)
- **Crítica (High):** Erros que impedem o uso, quebra visual grave ou violação de segurança/dados.
- **Média (Medium):** Inconsistência entre docs e código, falta de estados de loading/error.
- **Baixa (Low):** Débito técnico leve, melhorias estéticas não críticas, documentação defasada.

## 3. Definição de Pronto (DoD)
Toda issue de auditoria deve conter:
- Descrição clara do Drift.
- Referência ao documento ou ADR violada.
- Critérios de aceite técnicos.
