# Backlog Normalizado — Monitoramento Legislativo

Este documento contém o backlog oficial derivado do `story-map.md`, organizado por releases e prioridades.

---

## 🟢 RELEASE 1 — MVP (S6–S8)
*Meta: login → buscar proposição → ver detalhes → ver histórico de tramitação*

| ID | Issue | Prioridade | Esforço | Status |
|---|---|---|---|---|
| # | feat: ligar busca e filtros ao backend real | Alta | Pequeno | 📝 Todo |
| # | feat: endpoint GET /proposicoes/{id} e detalhe real | Alta | Pequeno | 📝 Todo |
| # | feat: card de tempo de tramitação com dados reais | Alta | Mínimo | 📝 Todo |
| # | feat: endpoint POST /auth/login com JWT | Alta | Médio | 📝 Todo |
| # | feat: endpoint POST /usuarios/cadastro | Alta | Pequeno | 📝 Todo |
| # | chore: script de seed com dados reais | Alta | Pequeno | 📝 Todo |
| # | chore: corrigir SenadoAdapter (campo data) | Alta | Mínimo | 📝 Todo |

---

## 🔵 RELEASE 2 — Produto Completo (S9–S12)
*Meta: cobertura ≥90%, coleta automatizada e timeline real*

| ID | Issue | Prioridade | Status |
|---|---|---|---|
| # | feat: entidade Tramitacao e endpoint de movimentações | Alta | 📝 Todo |
| # | feat: endpoints de breakdown para dashboard | Alta | 📝 Todo |
| # | feat: logout com invalidação no servidor | Alta | 📝 Todo |
| # | chore: worker de coleta batch diária | Alta | 📝 Todo |
| # | feat: tempo por fase com dados reais | Média | 📝 Todo |
| # | feat: filtros ativos afetando o dashboard | Média | 📝 Todo |
| # | chore: cache Redis para métricas | Média | 📝 Todo |
| # | feat: recuperação de senha por e-mail | Média | 📝 Todo |
| # | feat: estimativa de tempo de aprovação (IA) | Baixa | 📝 Todo |
| # | feat: bloqueio de conta (tentativas falhas) | Baixa | 📝 Todo |
| # | chore: documentar mapeamento de campos (ADR-005) | Baixa | 📝 Todo |
