# GEMINI.md - Resumo Operacional

## Objetivo

Monitoramento de Tempo de Tramitação de Leis (PL/PEC). Busca, acompanhamento e análise usando APIs da Câmara e Senado. Contexto acadêmico: sistema funcional + aprendizado de engenharia de software.

## Perfil Pedagógico

- Explique SEMPRE o "porquê", trade-offs e conceitos para estudo.
- Mudanças incrementais: analise → planeje → implemente (com aprovação).
- Nunca entregue código pronto sem contexto.
- Simplicidade > complexidade prematura.

## Regras Inegociáveis

1. **Layered Architecture**: presentation → application → domain → infrastructure.
2. **Domínio isolado**: regras de negócio não dependem de requisições HTTP ou lógicas de view.
3. **Adapters & Repositories**: toda integração externa (APIs, DB, cache) passa por interfaces em infrastructure.
4. **Resiliência**: tratar dados incompletos e falhas de APIs externas (Câmara/Senado).
5. **Frontend Feature-Based**: Nenhuma regra de negócio complexa no frontend. Componentes divididos por feature.

## Stack Principal

**Backend**: FastAPI + SQLModel + uv + Ruff + Pytest  
**Estrutura**: `src/presentation`, `src/application`, `src/domain`, `src/infrastructure`  
**Frontend**: React 18 + Vite + TypeScript + Tailwind CSS 3 + Vitest  
**Estrutura**: `src/app`, `src/shared`, `src/features`, `src/pages`  
**Infra**: PostgreSQL + Redis + GitHub Actions CI/CD  
**Métricas**: Squad Dashboard (Vite + Recharts + GitHub Actions Automations)

## Convenções Obrigatórias

- **Branches**: `feat/`, `fix/`, `docs/`, nunca `main` diretamente.
- **Commits**: Conventional Commits com **tipo em inglês** (`feat`, `fix`, `chore`, `refactor`) e **descrição em português no IMPERATIVO** (`adiciona`, `corrige`, `estabiliza`).
- **CI Verde**: não fazer merge sem CI aprovada.
- **Issues**: toda nova necessidade → issue aprovada → implementação.
  - No merge de PRs na branch `develop`, as issues associadas devem ter seu status atualizado para a label `status:done` e permanecer abertas.
  - O fechamento definitivo (Close) das issues só deve ocorrer quando as modificações forem integradas (mergeadas) na branch `main`.

## Estado Atual

Integração com APIs reais estabilizada; infra Docker e scripts de automação operacionais; CI/CD validando a integridade de todo o monorepo.

## Rigor de Implementação (Anti-Erro)

Para garantir sucesso na primeira tentativa ("First-Pass"), siga estas diretrizes:

1.  **Inspecione antes de Instanciar**: Antes de criar factories ou injetar serviços, **leia a assinatura completa do `__init__`** no arquivo de origem. Nunca assuma nomes de parâmetros (ex: `repository` vs `repo`).
2.  **Integridade de Novos Módulos**: Ao criar arquivos novos, verifique se **todos os tipos e classes** usados foram importados. Rode `ruff check <arquivo>` imediatamente após a criação.
3.  **Validação de Dependências**: Se uma task depende de outra recém-concluída, **re-leia os arquivos modificados** para atualizar seu mapa mental da estrutura, em vez de confiar no histórico de chat.

## O que evitar

- Respostas genéricas
- Novas dependências sem justificativa
- Refatorações em massa sem MVP funcional
- Abstrações enterprise prematuras
