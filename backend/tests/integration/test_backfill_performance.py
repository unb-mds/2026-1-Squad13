import time

import pytest
from sqlmodel import Session

from domain.entities.proposicao import Proposicao
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)


@pytest.mark.asyncio
async def test_batch_backfill_performance(db_session: Session):
    """
    Testa a performance do backfill de proposições em lote.
    Garante que o processamento/upsert de 10.000 proposições roda em menos de 5 minutos (300 segundos).
    """
    repo = SQLProposicaoRepository(db_session)

    # 1. Gera 10.000 proposições em memória
    proposicoes = [
        Proposicao(
            id=f"perf_{i}",
            tipo="PL",
            numero=str(1000 + i),
            ano=2026,
            autor=f"Autor Perf {i}",
            uf_autor="DF",
            orgao_origem="Câmara dos Deputados",
            status="Em Tramitação",
            ementa=f"Ementa de performance {i} contendo palavra fiscal",
            data_apresentacao="2026-01-01",
            data_ultima_movimentacao="2026-01-01",
            orgao_atual="CCJ",
            link_oficial=f"http://link.com/{i}",
            tags=["fiscal"],
            numero_assinaturas=5,
            numero_emendas=2,
            autor_e_poder_executivo=False,
            tema_economico=True,
        )
        for i in range(10000)
    ]

    # 2. Mede o tempo de execução do upsert em lote
    start_time = time.perf_counter()

    # Executa o lote
    repo.upsert_em_lote_por_numero_canonico(proposicoes)

    end_time = time.perf_counter()
    duration = end_time - start_time

    # 3. Asserções de integridade e tempo
    assert duration < 300.0, (
        f"Upsert de 10.000 proposições demorou {duration:.2f} segundos, excedendo o limite de 5 minutos."
    )
    print(
        f"\n⏱️ Performance do backfill: 10.000 proposições upsertadas em {duration:.4f}s."
    )
