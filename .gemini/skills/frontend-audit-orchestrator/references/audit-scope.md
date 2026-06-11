# Escopo da Auditoria Frontend

Definição do que deve ser analisado durante uma execução da skill de orquestração de auditoria.

## 1. Integridade de Design Tokens
- Uso correto das paletas `ink`, `volt`, `rose` e `amber`.
- Aplicação correta da tipografia (`DM Sans`, `Syne`, `JetBrains Mono`).
- Consistência de bordas, raios e sombras.

## 2. Arquitetura Feature-Based
- Componentes de feature isolados em suas pastas.
- Uso correto de `shared/components` para itens transversais.
- Ausência de lógica de negócio dentro de componentes atômicos de UI.

## 3. Padrões de Interface
- Implementação de Skeletons durante loading.
- Tratamento de Empty States em listas e gráficos.
- Padronização de Tooltips e Modais.

## 4. Documentação e Decisões
- Existência de documentação para novos componentes em `docs/frontend/04-componentes/`.
- Conformidade com as ADRs de frontend registradas.
- Sincronia entre o `walkthrough.md` e a realidade do código.
