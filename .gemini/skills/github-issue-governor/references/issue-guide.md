# Guia de Criação de Issues para IA (Governança e Dashboard)

Este documento define os padrões obrigatórios para a criação de issues neste repositório. O cumprimento rigoroso destas regras é essencial para que o **Squad Dashboard** processe as métricas de progresso, burndown e velocity corretamente.

## 1. Padrão de Título
Utilize o padrão **Conventional Commits** em português, em letras minúsculas (exceto siglas).
- `feat: <descrição>` - Novas funcionalidades.
- `fix: <descrição>` - Correção de bugs.
- `chore: <descrição>` - Tarefas técnicas, infraestrutura, CI/CD ou documentação.
- `refactor: <descrição>` - Melhorias de código sem mudança de comportamento.
- `test: <descrição>` - Adição ou correção de testes.

## 2. Estrutura do Body
O corpo da issue deve ser conciso e focado no "o quê" e no "porquê".
- **Descrição:** O que precisa ser feito.
- **Racional Técnico:** Por que isso é importante ou qual o impacto arquitetural.
- **Critérios de Aceite (Opcional):** Lista de requisitos para considerar a tarefa concluída.

## 3. Sistema de Labels (Obrigatório para o Dashboard)
Toda issue **DEVE** ter pelo menos uma label de cada categoria abaixo:

### A. Tipo (Type)
Define a natureza do trabalho.
- `type:feature`, `type:bug`, `type:chore`, `type:refactor`, `type:test`.

### B. Prioridade (Priority)
Define o impacto na sprint.
- `prio:high` (Impreterível), `prio:medium` (Desejável), `prio:low` (Se sobrar tempo).

### C. Status de Fluxo
Define a posição inicial no Kanban/Dashboard.
- `status:backlog` (Na fila, não planejado), `status:todo` (Pronto para puxar).

### D. Release
Define a versão de entrega.
- `release:R1` (MVP), `release:R2` (Produto Completo).

### E. Mapeamento de Feature (CRÍTICO)
Este campo alimenta os gráficos de progresso por Épico no dashboard. Escolha a label `feat:fX` que melhor se adapta:
- `feat:f1`: Busca de Proposições e Filtros.
- `feat:f2`: Visualização de Detalhes da Proposição.
- `feat:f3`: Dashboard de Análise e Gráficos.
- `feat:f4`: Coleta e Adapters (Câmara/Senado).
- `feat:f5`: Autenticação e Gestão de Usuários.
- `feat:f6`: Infraestrutura, Arquitetura e Segurança.
- `feat:f7`: Automação de Gestão (Squad Dashboard/CI).

## 4. Exemplo de Comando GH CLI
```bash
gh issue create \
  --title "chore: implementar logging estruturado nos adaptadores" \
  --body "Substituir prints por logging nativo para melhor observabilidade." \
  --label "type:chore,prio:medium,status:todo,release:R2,feat:f6"
```

---
*Este guia deve ser lido por qualquer agente de IA antes de realizar modificações no backlog do projeto.*
