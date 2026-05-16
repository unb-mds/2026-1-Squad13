# Guia de Métricas do Dashboard

## Burndown Semântico
Diferente de um burndown simples, nossa implementação separa:
- **Linha Ideal (Cinza Pontilhada):** Calculada no início da sprint/MVP. Mostra a tendência necessária para terminar o **escopo inicial** a tempo.
- **Trabalho Restante (Azul):** Itens abertos em cada data.
- **Escopo Total (Indigo Sombreado):** Soma do escopo inicial + itens adicionados durante a sprint. Permite visualizar claramente o "Scope Creep".

## Métricas de Fluxo (KPIs)
- **Scope Change:** Mede quanto o escopo cresceu desde o início. Útil para identificar problemas de refinamento.
- **Throughput:** Velocidade real de entrega (itens/dia). Ajuda a prever se o prazo será atingido.
- **Completion Rate:** Porcentagem do escopo total que já foi concluída.

## Como as datas são calculadas
O script analisa o `created_at` e `closed_at` de cada issue.
Se uma issue for fechada e reaberta, o dashboard refletirá o estado no final de cada dia.
A janela padrão é de **15 dias** para manter o foco na sprint atual.
