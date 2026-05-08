# ADR-002: PostgreSQL como banco de dados

**Data:** 2026-04-09  
**Status:** Aceita  
**Decisores:** Arquiteto, Dev  

---

## Contexto

O sistema precisa armazenar proposicoes, históricos de tramitação e calcular métricas temporais como:

- Tempo médio de tramitação por tema
- Tempo médio por relator
- Proposições paradas por período
- Evolução histórica do status de uma proposicao

Essas consultas envolvem agregações sobre datas e janelas temporais. A escolha do banco impacta diretamente a complexidade do código de análise.

---

## Decisão

Vamos usar **PostgreSQL** como banco de dados principal.

As funções de janela (`WINDOW FUNCTIONS`) do PostgreSQL resolvem as agregações temporais do projeto de forma elegante, sem precisar trazer todos os dados para o Python e calcular em memória.

Exemplo de consulta que o PostgreSQL resolve nativamente:

```sql
SELECT
  tema,
  AVG(dias_tramitacao) OVER (PARTITION BY tema) as media_por_tema,
  AVG(dias_tramitacao) OVER (PARTITION BY relator) as media_por_relator
FROM proposicoes;
```

---

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| PostgreSQL | Funções de janela, robusto, gratuito, suporte async | Requer servidor rodando (Docker) |
| SQLite | Zero configuração, arquivo único | Sem suporte real a funções de janela, sem concorrência |
| MongoDB | Flexível para JSONs das APIs | Agregações temporais complexas, sem joins nativos |
| MySQL | Familiar, amplamente usado | Funções de janela limitadas comparado ao PostgreSQL |

---

## Consequências

**Positivas:**
- Agregações temporais escritas em SQL, sem lógica extra em Python
- Suporte nativo a async via SQLAlchemy + asyncpg
- Fácil de subir localmente via Docker Compose

**Negativas / trade-offs:**
- Time precisa de Docker rodando no ambiente de desenvolvimento
- Requer configuração de variáveis de ambiente para conexão

**Riscos:**
- Migrations mal feitas podem corromper dados históricos coletados
- Mitigação: usar Alembic para controle de migrations com versionamento
ento
