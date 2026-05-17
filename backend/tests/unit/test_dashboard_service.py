import pytest
from sqlmodel import Session, SQLModel, create_engine
from domain.entities.proposicao import Proposicao
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)
from application.services.dashboard_service import DashboardService


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # P1: Aprovada, 100 dias (Sem atraso)
        p1 = Proposicao(
            id="1",
            tipo="PL",
            numero="1",
            ano=2024,
            autor="A",
            status="Aprovada",
            orgao_atual="CCJ",
            ementa="E1",
            data_apresentacao="2024-01-01",
            data_ultima_movimentacao="2024-01-01",
            tempo_total_dias=100,
        )
        # P2: Em tramitação, 200 dias (Atraso crítico), Orgao Lento
        p2 = Proposicao(
            id="2",
            tipo="PEC",
            numero="2",
            ano=2024,
            autor="B",
            status="Em tramitação",
            orgao_atual="LENTO",
            ementa="E2",
            data_apresentacao="2024-01-01",
            data_ultima_movimentacao="2024-01-01",
            tempo_total_dias=200,
        )
        session.add(p1)
        session.add(p2)
        session.commit()
        yield session


def test_obter_metricas_dashboard(session: Session):
    from infrastructure.repositories.sql_evento_tramitacao_repository import (
        SQLEventoTramitacaoRepository,
    )

    repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    service = DashboardService(repo, evento_repo)

    metricas = service.obter_metricas()

    assert metricas["totalProposicoes"] == 2
    assert metricas["totalAprovadas"] == 1
    assert metricas["totalEmTramitacao"] == 1
    assert metricas["proposicoesComAtraso"] == 1  # Apenas p2 tem > 180 dias
    assert metricas["tempoMedioTramitacao"] == 150  # (100 + 200) / 2
    assert metricas["comissaoMaiorTempo"] == "LENTO"
    assert metricas["comissaoMaiorTempoMedia"] == 200
