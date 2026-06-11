## Descrição
Migrar as chamadas síncronas realizadas pela biblioteca `requests` nos adaptadores da Câmara e do Senado para `httpx.AsyncClient`. Esta mudança deve vir acompanhada da conversão de métodos de serviços e controllers para `async def`, permitindo que o FastAPI gerencie o I/O de forma não bloqueante.

## Racional Técnico
Atualmente, as chamadas externas bloqueiam as threads do worker pool do FastAPI. Em cenários de alta latência das APIs governamentais ou alta concorrência, isso pode levar ao esgotamento de recursos e degradação da performance. O uso de `httpx` assíncrono permite maior throughput e a possibilidade de paralelizar chamadas independentes (ex: buscar dados na Câmara e Senado simultaneamente via `asyncio.gather`).

## Critérios de Aceite
- [ ] Bibliotecas `requests` removida dos adaptadores.
- [ ] Implementação de `httpx.AsyncClient` com timeouts configurados.
- [ ] Métodos dos adapters, serviços de aplicação e controllers convertidos para `async`.
- [ ] Testes de integração atualizados para suportar execução assíncrona (`pytest-asyncio`).
- [ ] Verificação de performance sob carga simulada (opcional, mas desejável).
