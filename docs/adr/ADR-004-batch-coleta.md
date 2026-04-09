# ADR-004: Batch diário como estratégia de coleta de dados

**Data:** 2026-04-09  
**Status:** Proposta  
**Decisores:** Arquiteto, Dev  

---

## Contexto

O sistema precisa coletar dados de tramitação das APIs da Câmara e do Senado. Existem duas estratégias possíveis: coletar sob demanda (quando o usuário pesquisa) ou coletar em batch periódico (independente do usuário).

A escolha impacta diretamente a experiência do usuário, a resiliência do sistema e a complexidade de implementação.

Fatores relevantes:
- Leis não tramitam de hora em hora — mudanças são diárias ou semanais
- As APIs públicas não têm SLA garantido e podem ficar instáveis
- O sistema precisa acumular histórico para calcular métricas temporais
- O usuário não deve esperar 3–5 segundos por uma pesquisa

---

## Decisão

Vamos usar **coleta em batch diária**, executada todo dia às 02h (horário de Brasília) por um worker Celery agendado via Celery Beat.

O usuário sempre lê dados do banco local. O sistema nunca chama as APIs externas durante uma requisição do usuário.

Fluxo:
```
02h → Celery Beat dispara → Worker coleta Câmara + Senado
    → Normaliza → Deduplica → Persiste no PostgreSQL
    → Invalida cache Redis
```

---

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| Sob demanda (on-demand) | Sempre dados frescos, simples de implementar | Lento para o usuário; falha da API = falha do sistema |
| Batch diário | Rápido para o usuário; sistema funciona offline | Dados podem ter até 24h de defasagem |
| Batch por hora | Dados mais frescos que diário | Sobrecarga desnecessária nas APIs públicas |
| Webhook / streaming | Dados em tempo real | APIs legislativas não oferecem webhook |

---

## Consequências

**Positivas:**
- Usuário sempre recebe resposta rápida (lê do banco, não da API)
- Sistema funciona mesmo quando a Câmara ou o Senado está fora do ar
- Histórico acumulado permite calcular métricas temporais corretamente
- Coleta fora do horário comercial reduz impacto nas APIs públicas

**Negativas / trade-offs:**
- Dados podem ter até 24h de defasagem em relação à fonte
- Requer Celery + Redis como infraestrutura adicional
- Coleta inicial (histórico completo) pode demorar e exige paginação cuidadosa

**Riscos:**
- Se o worker falhar silenciosamente, os dados ficam desatualizados sem aviso
- Mitigação: logging de cada execução + alerta quando a última coleta bem-sucedida tiver mais de 26h
