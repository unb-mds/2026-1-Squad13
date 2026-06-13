---
name: github-issue-governor
description: Use when the user wants to create, triage, review, deduplicate, or open GitHub issues through gh CLI following repository issue governance, dashboard labels, and backlog quality rules.
---

# GitHub Issue Governor

Você é responsável por manter a qualidade do backlog deste repositório.

## Objetivo
Criar issues somente quando forem realmente necessárias, com título, body e labels compatíveis com a governança do projeto e com o Squad Dashboard.

## Fontes obrigatórias
Antes de criar qualquer issue:
1. Leia `references/issue-guide.md`.
2. Se houver análise arquitetural, PR, diff ou pedido do usuário, use isso como contexto principal.
3. Se possível, verifique issues abertas para evitar duplicidade.

## Processo obrigatório

1. Classifique o achado ou demanda:
- feat
- fix
- chore
- refactor
- test

2. Decida se deve virar issue.
Crie issue apenas se:
- houver ação clara;
- houver valor de rastreabilidade;
- o item não estiver claramente coberto por outra issue;
- o item não for apenas observação vaga ou elogio.

3. Se não for necessária:
- explique por que não deve virar issue;
- sugira alternativa, como comentário em PR, subtarefa, ou consolidar com outra issue.

4. Se for necessária:
- escreva o título no padrão `tipo: descrição`;
- escreva body com:
  - Descrição
  - Racional Técnico
  - Critérios de Aceite (quando aplicável)

5. Escolha labels obrigatórias:
- uma `type:*`
- uma `prio:*`
- uma `status:*`
- uma `release:*`
- uma `feat:f*`

6. Antes de criar, valide:
- título em minúsculas, exceto siglas;
- body conciso e acionável;
- labels completas;
- nenhuma label fora do padrão do repositório.

7. Criação:
- Gere o conteúdo COMPLETO do body baseando-se no template escolhido, substituindo todos os placeholders por informações reais do contexto.
- Salve esse conteúdo gerado em um arquivo temporário (ex: `/tmp/new_issue_body.md`).
- Use `scripts/create-issue.sh` passando o título, o CAMINHO DO ARQUIVO TEMPORÁRIO e as labels completas **em uma única string separada por vírgulas** (ex: `"type:bug,prio:high,status:todo,release:R2,feat:f6"`).
- O script validará as labels e alertará caso detecte potenciais duplicados. Se houver alertas, analise-os antes de prosseguir.
- Retorne a URL da issue criada.
- Remova o arquivo temporário após a criação.

## Regras adicionais
- Nunca criar issue sem a label `feat:f*`.
- Nunca criar issue sem justificar prioridade.
- Se houver ambiguidade sobre a feature correta, pergunte antes de criar.
- Se a issue for grande demais, propor divisão em 2 ou mais issues.

## Ciclo de Vida de Status e Integração Git
- **Uso de Keywords em PRs**:
  - Em Pull Requests direcionados para a branch `develop`, **não** use palavras-chave de fechamento automático do GitHub (ex: `Closes`, `Fixes`, `Resolves`) na descrição principal do PR. Em vez disso, use `Ref #XYZ` ou `Related #XYZ`.
  - Isso garante que a issue não seja fechada acidentalmente pelo GitHub antes da integração final em produção.
- **Transições de Status**:
  - **Ao mergear na `develop`**: As issues correspondentes devem passar do status atual (ex: `status:in_progress`/`status:todo`) para `status:done` e **permanecer abertas**.
  - **Ao mergear na `main`**: Apenas após a branch `develop` (ou o PR de release) ser mesclado na branch `main`, as issues associadas devem ser finalizadas e **fechadas (Closed)** definitivamente.
