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
| #92 | feat: logout com invalidação no servidor | Alta | 📝 Todo |
| #87 | chore: worker de coleta batch diária | Alta | 📝 Todo |
| #89 | feat: tempo por fase com dados reais | Média | 📝 Todo |
| #91 | feat: filtros ativos afetando o dashboard | Média | 📝 Todo |
| #94 | chore: cache Redis para métricas | Média | 📝 Todo |
| #86 | feat: recuperação de senha por e-mail | Média | 📝 Todo |
| #96 | feat: estimativa de tempo de aprovação (IA) | Baixa | 📝 Todo |
| #93 | feat: bloqueio de conta (tentativas falhas) | Baixa | 📝 Todo |
| #95 | chore: documentar mapeamento de campos (ADR-005) | Baixa | 📝 Todo |
