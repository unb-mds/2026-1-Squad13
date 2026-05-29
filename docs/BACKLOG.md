# Backlog Normalizado — Monitoramento Legislativo

Este documento contém o backlog oficial derivado do `story-map.md`, organizado por releases e prioridades.

---

## 🟢 RELEASE 1 — MVP (S6–S8)
*Meta: login → buscar proposição → ver detalhes → ver histórico de tramitação*

| ID | Issue | Prioridade | Esforço | Status |
|---|---|---|---|---|
| #40 | feat: ligar busca e filtros ao backend real | Alta | Pequeno | ✅ Done |
| #43 | feat: endpoint GET /proposicoes/{id} e detalhe real | Alta | Pequeno | ✅ Done |
| #44 | feat: endpoint POST /auth/login com JWT | Alta | Médio | ✅ Done |
| #82 | feat: endpoint POST /usuarios/cadastro | Alta | Pequeno | ✅ Done |
| #45 | chore: script de seed com dados reais | Alta | Pequeno | ✅ Done |
| #46 | fix: corrigir SenadoAdapter (campo data) | Alta | Mínimo | ✅ Done |

---

## 🔵 RELEASE 2 — Produto Completo (S9–S12)
*Meta: cobertura ≥90%, coleta automatizada e timeline real*

| ID | Issue | Prioridade | Status |
|---|---|---|---|
| #88 | feat: modelo analítico EventoTramitacao e endpoint de movimentações | Alta | ✅ Done |
| #90 | feat: endpoints de breakdown para dashboard | Alta | ✅ Done |
| #130 | feat: criar AgregarPorFaseService para períodos de fase | Média | 📝 Todo |
| #131 | feat: suporte ao query param modo no endpoint de movimentações | Média | 📝 Todo |
| #165 | feat: infraestrutura e banco para métricas de atraso | Alta | 📝 Todo |
| #166 | feat: serviço de cálculo de métricas (IAR, IAF, IEI) | Alta | 📝 Todo |
| #167 | feat: worker de atualização de métricas e baselines | Alta | 📝 Todo |
| #168 | feat: endpoints de métricas de atraso no dashboard e detalhe | Alta | 📝 Todo |
| #169 | feat: interface visual de status de atraso e explicabilidade | Alta | 📝 Todo |
| #87 | chore: worker de coleta batch diária | Alta | 📝 Todo |
| #89 | feat: tempo por fase com dados reais | Média | 🏗️ In Progress |
| #91 | feat: filtros ativos afetando o dashboard | Média | 📝 Todo |
| #155 | feat: implementa cache distribuído (Redis) para períodos de fase | Média | 📝 Todo |
| #156 | feat: integra modelo NLP leve para classificação semântica de eventos | Baixa | 📝 Todo |
| #132 | chore: refatora injeção de dependência nos serviços de aplicação | Média | 📝 Todo |
| #141 | chore: refatora injeção de dependência nos Controllers | Média | 📝 Todo |
| #139 | test: implementa testes de contrato (VCR) para APIs governamentais | Média | 📝 Todo |
| #144 | test: valida filtros JSONB de tags em ambiente Postgres real | Média | 📝 Todo |
| #145 | test: implementa cobertura de testes para GerarEstimativaUseCase | Média | 📝 Todo |
| #170 | chore: remover endpoints de autenticação, serviços e migrações no backend | Alta | 📝 Todo |
| #171 | refactor: desativar AuthProvider, login/cadastro e rotas privadas no frontend | Alta | 📝 Todo |
| #172 | refactor: redesenhar frontend para dashboard analítico de investigação sóbrio | Alta | 📝 Todo |
| #173 | chore: estabelecer rotinas de pareamento e governança para equilíbrio de commits | Média | 📝 Todo |


