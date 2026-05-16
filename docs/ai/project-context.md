# Contexto do Projeto

## Visão Geral

O projeto **Monitoramento de Tempo de Tramitação de Leis** tem como objetivo permitir busca, acompanhamento e análise de proposições legislativas (PL e PEC), utilizando dados públicos oficiais. 

O produto é desenvolvido em contexto acadêmico, com foco em entrega funcional e aprendizado prático de engenharia de software e arquitetura.

## Ecossistema de Software

O repositório abriga três subprojetos principais:
1. **Backend (`/backend`)**: API de integração e processamento de regras de negócio.
2. **Frontend (`/frontend`)**: Interface web analítica para o usuário final.
3. **Squad Dashboard (`/squad-dashboard`)**: Ferramenta interna da equipe para monitoramento de métricas ágeis, burndown e commits via automação do GitHub Actions.

## Escopo do MVP (Produto Principal)

O MVP deve priorizar:
- Busca e normalização de proposições legislativas (Câmara e Senado).
- Acompanhamento de tramitação baseado no modelo analítico `EventoTramitacao`.
- Classificação de eventos legislativos (20 tipos normalizados) e determinação de fases analíticas (8 fases).
- Cálculo dinâmico de métricas para o Dashboard (tempo por fase, gargalos, etc).
- Arquitetura resiliente a falhas de comunicação com órgãos públicos.

## Diretrizes de Arquitetura

O backend segue **Layered Architecture**, dividindo o código em quatro camadas isoladas que conversam apenas com a camada inferior imediata:
- `presentation`: FastAPI, rotas, validações HTTP.
- `application`: Orquestração de casos de uso (Services, ex: `NormalizarTramitacaoService`).
- `domain`: Regras de negócio, cálculos (ex: `ClassificarEventoService`, `EventoTramitacao`).
- `infrastructure`: Banco de dados (SQLModel), APIs externas (via Adapters), cache.

O frontend segue a arquitetura **Feature-Based**:
- `app`: Configurações globais e providers.
- `features`: Funcionalidades isoladas de negócio.
- `pages`: Composição de features e navegação.
- `shared`: Componentes UI reutilizáveis.

## Stack Tecnológica

### Backend
- **Linguagem/Framework:** Python 3.12+ com FastAPI.
- **Persistência:** PostgreSQL gerenciado via SQLModel.
- **Gerenciamento:** `uv` para dependências.
- **Qualidade:** Ruff (lint) e Pytest (testes unitários e de integração).

### Frontend
- **Linguagem/Framework:** React 18 com Vite e TypeScript.
- **Estilização:** Tailwind CSS 3.
- **Qualidade:** ESLint e Vitest.

### Infra e CI/CD
- GitHub Actions para pipelines independentes de Backend, Frontend e Squad Dashboard.
- Coleta de dados planejada via jobs periódicos em batch.

## Convenções de Desenvolvimento

- **Commits:** Conventional Commits em português e no imperativo (ex: `adiciona endpoint`, `corrige erro no adapter`).
- **Issues:** Rastreamento rigoroso de tarefas para alimentar as métricas de projeto. Nenhuma implementação deve começar sem uma issue correlata.
- **Branches:** Padrão `feat/`, `fix/`, `docs/`. Proibido commit direto na `main`. Apenas merges com CI verde.

## Estado Atual

O projeto encontra-se em fase de estabilidade e expansão:
- Integração com APIs reais (Câmara e Senado) concluída com tratamento de erros e resiliência.
- Infraestrutura de banco de dados e cache (Postgres/Redis) totalmente operacional via Docker.
- Pipeline de métricas do Squad Dashboard 100% automatizado.
