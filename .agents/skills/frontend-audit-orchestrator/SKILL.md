---
name: frontend-audit-orchestrator
description: Use para auditar, comparar e diagnosticar a consistência entre a documentação de frontend, ADRs e o código real do LexTrack.
---

# Frontend Audit Orchestrator

Você é responsável por identificar o "Drift" (desvio) entre o que foi planejado/documentado e o que está de fato implementado no frontend do LexTrack. Sua missão é manter o backlog de UI organizado e priorizado.

## Quando Usar
- Auditorias periódicas de consistência visual e estrutural.
- Diagnóstico de dívida técnica ou código legado no frontend.
- Organização de backlog após grandes refatorações ou mudanças de design.
- Verificação de conformidade com as diretrizes de `docs/frontend/`.

## Quando NÃO Usar
- Implementação direta de funcionalidades.
- Auditoria de backend ou infraestrutura.

## Entradas Esperadas
- Documentação em `docs/frontend/`.
- ADRs em `docs/adr/`.
- Código-fonte em `/frontend/src/`.
- `walkthrough.md` (Auditoria anterior, se disponível).

## Processo de Auditoria

### 1. Coleta de Artefatos
- Utilize `scripts/collect-audit-inputs.sh` para reunir os arquivos-chave. Se o processo demorar, monitore sua execução como uma tarefa em segundo plano.
- Mapeie as features ativas e componentes compartilhados.

### 2. Análise de Drift
Compare a documentação contra o código buscando desvios nas categorias de `references/drift-categories.md`:
- **Visual:** Cores, fontes, espaçamentos.
- **Estrutural:** Pastas, padrões de arquivos.
- **Funcional:** Comportamento de componentes vs especificação.
- **Governança:** Ausência de docs para novas implementações.

### 3. Geração de Relatório
- Preencha o `templates/audit-report-template.md` com os achados.
- Realize uma Análise de Lacunas (Gap Analysis) usando `templates/gap-analysis-template.md`.
- **Geração de Artefato:** Crie este relatório de auditoria final em formato Markdown como um artefato do Antigravity CLI (com metadados `UserFacing: true`) para que possa ser lido interativamente pelo time de desenvolvimento.

### 4. Gestão de Backlog
- Transforme os achados em issues acionáveis usando `templates/issue-template.md`.
- Priorize as issues seguindo as regras de `references/backlog-rules.md`.
- Sugira quais documentos em `docs/frontend/` precisam de atualização imediata.

## Saída Esperada
Um relatório executivo de auditoria contendo:
- Resumo do estado de saúde do frontend.
- Lista de Drifts identificados.
- Backlog de issues priorizadas para correção.
