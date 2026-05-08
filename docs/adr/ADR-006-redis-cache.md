# ADR-006: Redis para cache de respostas

**Data:** 2026-04-09  
**Status:** Aceita  
**Decisores:** Arquiteto, Dev  

---

## Contexto

Mesmo com a coleta em batch (ADR-004), algumas consultas do backend são computacionalmente pesadas ou repetidas com frequência, como:

- Listagem de proposicoes paradas por tema (consulta agregada)
- Ranking de relatores com mais proposicoes paradas
- Dados do dashboard principal (acessado por todos os usuários)

Sem cache, cada requisição do usuário executa uma query no banco. Com o volume de dados legislativos históricos, algumas queries podem demorar mais do que o aceitável.

Adicionalmente, o Celery já precisa do Redis como broker de mensagens (requisito do ADR-004). Usar o mesmo Redis para cache não adiciona dependência nova.

---

## Decisão

Vamos usar **Redis** como camada de cache para respostas de consultas frequentes e pesadas.

Estratégia:
- TTL padrão: 1 hora para consultas gerais
- Invalidação ativa: após cada coleta bem-sucedida (ADR-004), o worker invalida as chaves de cache afetadas
- Cache key pattern: `{recurso}:{parametros}` — ex: `proposicoes_paradas:educacao`

```python
# infrastructure/cache/redis_cache.py
class RedisCache:
    def get(self, key: str): ...
    def set(self, key: str, value, ttl: int = 3600): ...
    def invalidate(self, pattern: str): ...
```

---

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| Redis (escolhida) | Já usado pelo Celery; TTL nativo; rápido | Mais um serviço para operar |
| Cache em memória (dict Python) | Zero configuração | Não persiste entre reinicializações; não compartilhado entre workers |
| Cache no PostgreSQL | Sem serviço extra | Derrotaria o propósito (sobrecarga no banco) |
| Sem cache | Simplicidade máxima | Queries lentas com volume histórico crescente |

---

## Consequências

**Positivas:**
- Consultas frequentes respondem em milissegundos em vez de segundos
- Redis já está na infraestrutura como broker do Celery — sem custo extra de operação
- TTL garante que dados desatualizados expiram automaticamente

**Negativas / trade-offs:**
- Time precisa gerenciar invalidação de cache corretamente — cache desatualizado é pior que sem cache
- Adiciona complexidade de debugging (comportamento diferente com e sem cache frio)

**Riscos:**
- Cache não invalidado após coleta pode servir dados do dia anterior como se fossem atuais
- Mitigação: invalidação explícita no final de cada job de coleta bem-sucedido, com log confirmando
- Se o Redis cair, o sistema deve degradar graciosamente (buscar no banco sem cache), não travar
, não travar
