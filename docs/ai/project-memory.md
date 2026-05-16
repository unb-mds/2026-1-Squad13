# Memória Evolutiva do Projeto

## Finalidade

Este documento registra decisões técnicas, arquiteturais e de fluxo já materializadas e consolidadas no código e na infraestrutura do repositório. Ele serve para orientar implementações futuras evitando retrocessos.

## Critérios de Registro

**Toda decisão documentada aqui deve estar apoiada em evidências reais do repositório (arquivos, configurações, workflows).**

Devem ser registrados:
- decisões arquiteturais consolidadas;
- convenções técnicas aprovadas e persistentes;
- integrações relevantes adotadas de forma estável;
- mudanças duráveis em workflows, CI/CD ou organização do projeto;
- regras de negócio persistentes que impactem futuras implementações.

Não devem ser registrados:
- bugs pontuais;
- experimentos descartados;
- tarefas temporárias;
- discussões ainda não aprovadas;
- descrições completas de atividades operacionais sem impacto duradouro.

## Formato de Registro

Sempre que uma nova decisão persistente for adicionada, o registro deve seguir esta estrutura:

### [AAAA-MM] Título da decisão
**Evidência:** arquivos, trechos, pastas, workflows ou configs que sustentam a decisão.  
**Decisão:** descrição objetiva do que está de fato consolidado.  
**Justificativa:** motivo principal da decisão (o "porquê" pedagógico).  
**Impacto:** como essa decisão deve orientar implementações futuras.

---

## Decisões Consolidadas

### [2026-05] Migração para Modelo Analítico de Tramitação (`EventoTramitacao`)
**Evidência:** Diretórios `backend/src/domain/entities/evento_tramitacao.py`, `backend/src/domain/classificar_evento.py` e `docs/MIGRATION_SCOPE.md`.  
**Decisão:** Substituição do modelo legado de `Tramitacao` pelo modelo analítico, que classifica cada tramitação por 20 tipos de eventos normalizados e 8 fases legislativas.  
**Justificativa:** APIs da Câmara e Senado retornam textos verbosos e variados, inviabilizando agregações numéricas no dashboard e detecção de gargalos. A normalização no domínio resolve isso.  
**Impacto:** Métricas de tempo e dashboards não utilizam mais os campos das APIs diretamente; todos os cálculos são baseados no `TipoEvento` e `FaseAnalitica`.

### [2026-05] Layered Architecture como contrato estrito de backend
**Evidência:** Estrutura isolada em `backend/src/` com pastas `presentation`, `application`, `domain` e `infrastructure`.
**Decisão:** O domínio não conhece frameworks HTTP nem de acesso direto à rede. Controllers em `presentation` delegam para `application`.
**Justificativa:** Garantir testabilidade unitária e isolamento de dependências externas variáveis.
**Impacto:** Novas rotas devem criar um "Service" correspondente em `application`, nunca processando regra de negócio no controller.

### [2026-05] SQLModel como unificador de Domínio e Persistência
**Evidência:** `backend/pyproject.toml` e uso em `backend/src/infrastructure/database.py`.
**Decisão:** O projeto utiliza SQLModel no MVP para que os modelos de domínio sejam os mesmos da persistência relacional.
**Justificativa:** O overhead de mapeamento manual (Clean Architecture pura) foi preterido em favor de velocidade de entrega para o MVP, conforme ADR-001.
**Impacto:** As entidades devem continuar sendo decoradas com funcionalidades do SQLModel sem que isso seja considerado violação grave da arquitetura na fase atual.

### [2026-05] Isolamento de integrações com Adapter Pattern
**Evidência:** Existência de `camara_adapter.py`, `senado_adapter.py` e suas versões mock em `backend/src/infrastructure/adapters/`.
**Decisão:** Toda chamada HTTP para a Câmara ou Senado é envelopada por um Adapter que normaliza os dados para o formato interno do projeto.
**Justificativa:** Minimizar o impacto de mudanças nas respostas das APIs governamentais.
**Impacto:** Nenhuma lógica de aplicação ou negócio deve instanciar `httpx` ou `requests` diretamente. O consumo deve ser via injeção dos Adapters.

### [2026-05] Automação de Métricas de Engenharia (Squad Dashboard)
**Evidência:** Subprojeto em `/squad-dashboard` e workflow em `.github/workflows/update-squad-dashboard-data.yml`.
**Decisão:** O acompanhamento de burndown, progresso de features e velocidade de commits é automatizado via API do GitHub Actions e não requer preenchimento manual do time.
**Justificativa:** Fornecer dados reais de engenharia de software para avaliação acadêmica e análise do time.
**Impacto:** A gestão de labels (`feat:`, `status:`) nas issues é crítica, pois alimenta diretamente o parser de progresso do dashboard.

### [2026-05] Pirâmide de testes segmentada no backend
**Evidência:** Diretórios `backend/tests/unit/` e `backend/tests/integration/` contendo arquivos consolidados de teste (`conftest.py`, `test_camara_adapter.py`).
**Decisão:** Os testes de integração (acesso a BD, APIs mockadas) são estritamente separados dos testes unitários (execução em memória pura).
**Justificativa:** Garantir CI rápida (unitários) enquanto mantém garantia de funcionamento do fluxo completo (integração).
**Impacto:** Novos Adapters de rede ou Repositórios de banco exigem testes na pasta `integration`. Lógicas de cálculo ou formatação devem ir para `unit`.

### [2026-05] Validação Blindada e Automação de Ambiente
**Evidência:** Scripts `start_dev.sh`, `test_all.sh` e configuração do Ruff/Vitest.
**Decisão:** Uso de scripts de entrada única para subir o ambiente e validar todo o monorepo. Adoção do Ruff (backend) e Vitest (frontend) como padrões de qualidade.
**Justificativa:** Reduzir o atrito no onboarding e garantir que nenhum commit quebre a integridade do monorepo.
**Impacto:** O CI bloqueia merges sem a "Validação Blindada" (lint + tipos + testes) aprovada em ambos os subprojetos.
