# ADR-003: FastAPI como framework do backend

**Data:** 2026-04-09  
**Status:** Proposta  
**Decisores:** Arquiteto, Dev, PO  

---

## Contexto

O backend precisa expor uma API REST que o frontend consome. A principal carga do sistema é I/O: chamadas às APIs externas da Câmara e do Senado, que podem demorar de 1 a 5 segundos por requisição.

O time já conhece Python de disciplinas anteriores. Precisamos de um framework que:

- Suporte operações assíncronas (async/await) nativamente
- Gere documentação da API automaticamente para integração com o frontend
- Tenha boa tipagem para reduzir erros entre camadas
- Seja simples o suficiente para um projeto semestral

---

## Decisão

Vamos usar **FastAPI** como framework da camada de Apresentação.

O suporte nativo a `async/await` é decisivo: enquanto o sistema aguarda resposta da API da Câmara, o servidor pode processar outras requisições em paralelo, sem bloquear. A geração automática de Swagger/OpenAPI permite que o designer integre o frontend sem esperar o dev documentar manualmente cada endpoint.

---

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| FastAPI | async nativo, Swagger automático, tipagem com Pydantic | Mais recente, menos material em português |
| Django | ORM completo, admin grátis, muito material | Síncrono por padrão, overhead pesado para uma API |
| Django REST Framework | Familiar, robusto | Herda as limitações síncronas do Django |
| Flask | Simples, muito material | Sem async nativo, sem documentação automática |

---

## Consequências

**Positivas:**
- Chamadas às APIs externas não bloqueiam o servidor
- Swagger gerado automaticamente em `/docs` — frontend integra sem reuniões extras
- Pydantic garante que os dados entre camadas estão no formato correto

**Negativas / trade-offs:**
- Time precisa aprender Pydantic para validação e serialização
- Painel admin do Django não está disponível — criar telas admin manualmente se necessário

**Riscos:**
- Se precisarmos de ORM complexo, SQLAlchemy async tem curva de aprendizado adicional
- Mitigação: usar SQLAlchemy com exemplos já prontos no repositório
