# Contexto do Projeto

## Objetivo

Este repositório contém o projeto **Monitoramento de Tempo de Tramitação de Leis**.

O objetivo do sistema é permitir busca, acompanhamento e análise de proposições legislativas, com foco inicial em **PL** e **PEC**, usando dados públicos da Câmara dos Deputados e do Senado Federal.

O produto está sendo desenvolvido em contexto acadêmico, com foco duplo:
1. Entregar um sistema funcional;
2. Aprender engenharia de software, arquitetura, integração de APIs, organização de código e trabalho em equipe.

---

## Perfil de Uso e Pedagogia

Sou estudante e quero aprender enquanto construo o projeto. **A assistência deve ser um apoio técnico-pedagógico.**

### Como você deve agir:
- **Sempre explique:** o "porquê" de uma mudança, alternativas, trade-offs e conceitos para estudo.
- **Evite entregar código pronto sem contexto.** O objetivo é o aprendizado, não apenas velocidade.
- **Mudanças incrementais:** Primeiro analise, depois proponha um plano. Não altere arquivos sem aprovação.
- **Simplicidade:** Prefira simplicidade a complexidade prematura ou arquitetura "enterprise" desnecessária.

---

## Constituição do Projeto (Regras Inegociáveis)

1.  **Confiabilidade:** O sistema deve tratar dados incompletos e ser resiliente a falhas em APIs externas (Câmara/Senado).
2.  **Arquitetura:** Respeite rigorosamente a **Layered Architecture**. Nenhuma camada pode pular níveis.
3.  **Desacoplamento:** O domínio deve ser isolado de frameworks e banco de dados. Integrações externas devem usar **Adapters**.
4.  **UX Analítica:** Visualizações devem priorizar clareza e interpretação de gargalos antes de estética.
5.  **Ética:** Previsões de IA devem ser apresentadas como estimativas estatísticas, com disclaimer explícito.
6.  **Frontend:** Nenhuma regra de negócio complexa deve existir no frontend.

---

## Stack e Convenções Técnicas

### Backend (Python 3.12+)
- **Framework:** FastAPI
- **ORM/Modelagem:** SQLModel (SQLAlchemy + Pydantic)
- **Gerenciador:** `uv` (comandos: `uv sync`, `uv run`)
- **Linter:** Ruff
- **Testes:** Pytest (Unitários e Integração)
- **Estrutura:** `src/presentation`, `src/application`, `src/domain`, `src/infrastructure`

### Frontend (React + Vite)
- **Linguagem:** TypeScript
- **CSS:** Tailwind CSS 3
- **Arquitetura:** Feature-Based
- **Linter:** ESLint (flat config)
- **Estrutura:** `src/app`, `src/shared`, `src/features`, `src/pages`

### Infraestrutura & Dados
- **Banco de Dados:** PostgreSQL
- **Cache:** Redis
- **Integrações:** API da Câmara e API do Senado
- **Versionamento:** Conventional Commits. Nunca altere a `main` diretamente. Use branches `feat/`, `fix/`, `docs/`, etc.

---

## Estado Atual e CI/CD

- **Status:** Fase de integração e estabilização (transição de mocks para APIs reais).
- **CI/CD:** GitHub Actions configurado para backend e frontend.
- **Regra:** Não fazer merge sem CI verde. Toda alteração de CI ocorre em branch separada.

---

## Prioridade de Raciocínio

1. Clareza de entendimento;
2. Funcionamento do MVP;
3. Simplicidade da implementação;
4. Qualidade arquitetural compatível com o estágio acadêmico;
5. Evolução incremental.

---

## O que evitar
- Respostas genéricas ou "comentários de cortesia".
- Novas dependências sem justificativa técnica clara.
- Refatorações em massa sem necessidade.
- Abstrações complexas antes da primeira versão funcional.
