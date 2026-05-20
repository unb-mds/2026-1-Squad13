import pytest
from sqlmodel import Session, SQLModel, create_engine
from infrastructure.database.models.proposicao_model import ProposicaoModel
from infrastructure.repositories.sql_dashboard_repository import SQLDashboardRepository
from domain.constants import LIMITE_DIAS_ATRASO


@pytest.fixture(name="session")
def session_fixture():
    """Cria um banco de dados em memória para cada teste."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_obter_metricas_gerais(session: Session):
    repo = SQLDashboardRepository(session)

    # Adiciona dados de teste
    # P1: Aprovada, 100 dias (Sem atraso)
    p1 = ProposicaoModel(
        id="1",
        tipo="PL",
        numero="1",
        ano=2024,
        autor="Autor A",
        status="Aprovada",
        orgao_atual="CCJ",
        ementa="E1",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        tempo_total_dias=100,
    )
    # P2: Em tramitação, atraso crítico (LIMITE + 20), Orgao Lento
    p2 = ProposicaoModel(
        id="2",
        tipo="PEC",
        numero="2",
        ano=2024,
        autor="Autor B",
        status="Em tramitação",
        orgao_atual="LENTO",
        ementa="E2",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        tempo_total_dias=LIMITE_DIAS_ATRASO + 20,
    )

    session.add(p1)
    session.add(p2)
    session.commit()

    metricas = repo.obter_metricas_gerais(None)

    assert metricas["totalProposicoes"] == 2
    assert metricas["totalAprovadas"] == 1
    assert metricas["totalEmTramitacao"] == 1
    assert metricas["proposicoesComAtraso"] == 1
    assert metricas["tempoMedioTramitacao"] == (100 + LIMITE_DIAS_ATRASO + 20) // 2
    assert metricas["comissaoMaiorTempo"] == "LENTO"


def test_obter_metricas_com_filtros(session: Session):
    repo = SQLDashboardRepository(session)

    p1 = ProposicaoModel(
        id="1",
        tipo="PL",
        numero="1",
        ano=2024,
        autor="A",
        status="Aprovada",
        orgao_atual="O1",
        ementa="E1",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        tempo_total_dias=10,
    )
    p2 = ProposicaoModel(
        id="2",
        tipo="PEC",
        numero="2",
        ano=2024,
        autor="B",
        status="Rejeitada",
        orgao_atual="O2",
        ementa="E2",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        tempo_total_dias=20,
    )

    session.add(p1)
    session.add(p2)
    session.commit()

    # Filtro por tipo
    met_pl = repo.obter_metricas_gerais({"tipo": "PL"})
    assert met_pl["totalProposicoes"] == 1
    assert met_pl["totalAprovadas"] == 1

    # Filtro por busca
    met_busca = repo.obter_metricas_gerais({"busca": "E2"})
    assert met_busca["totalProposicoes"] == 1
    assert met_busca["totalRejeitadas"] == 1


def test_obter_dados_graficos(session: Session):
    repo = SQLDashboardRepository(session)

    p1 = ProposicaoModel(
        id="1",
        tipo="PL",
        numero="1",
        ano=2024,
        autor="A",
        status="Aprovada",
        orgao_atual="O1",
        ementa="E1",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        tempo_total_dias=10,
    )
    p2 = ProposicaoModel(
        id="2",
        tipo="PL",
        numero="2",
        ano=2024,
        autor="B",
        status="Aprovada",
        orgao_atual="O1",
        ementa="E2",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        tempo_total_dias=30,
    )

    session.add(p1)
    session.add(p2)
    session.commit()

    dados_tipo = repo.obter_dados_tipo(None)
    assert len(dados_tipo) == 1
    assert dados_tipo[0]["tipo"] == "PL"
    assert dados_tipo[0]["quantidade"] == 2
    assert dados_tipo[0]["tempoMedio"] == 20

    dados_status = repo.obter_dados_status(None)
    assert any(d["status"] == "Aprovada/Sancionada" for d in dados_status)
