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
- **Commits**: Conventional Commits em **português** e **IMPERATIVO** (`adiciona`, `corrige`, `refatora`).
- **CI Verde**: não fazer merge sem CI aprovada.
- **Issues**: toda nova necessidade → issue aprovada → implementação.

## Estado Atual

Integração com APIs reais estabilizada; infra Docker e scripts de automação operacionais; CI/CD validando a integridade de todo o monorepo.

## O que evitar

- Respostas genéricas
- Novas dependências sem justificativa
- Refatorações em massa sem MVP funcional
- Abstrações enterprise prematuras
