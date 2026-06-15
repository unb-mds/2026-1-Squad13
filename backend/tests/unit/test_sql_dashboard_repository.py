import pytest
from sqlmodel import Session, SQLModel, create_engine

from domain.constants import LIMITE_DIAS_ATRASO
from infrastructure.database.models.proposicao_model import ProposicaoModel
from infrastructure.repositories.sql_dashboard_repository import SQLDashboardRepository


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
    p1 = ProposicaoModel(
        id="1",
        tipo="PL",
        numero="1",
        ano=2024,
        autor="A",
        status="Aprovada",
        orgao_atual="LENTO",
        ementa="E1",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        tempo_total_dias=100 + LIMITE_DIAS_ATRASO,
        indice_atraso_relativo=1.5,
        indice_espera_improdutiva=0.5,
    )
    p2 = ProposicaoModel(
        id="2",
        tipo="PEC",
        numero="2",
        ano=2024,
        autor="B",
        status="Em tramitação",
        orgao_atual="RAPIDO",
        ementa="E2",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        tempo_total_dias=20,
        indice_atraso_relativo=0.5,
        indice_espera_improdutiva=0.1,
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
    assert metricas["iarMedio"] == 1.0  # (1.5 + 0.5) / 2
    assert metricas["ieiMedio"] == 0.3  # (0.5 + 0.1) / 2
    assert metricas["percentualAtrasadas"] == 50
    assert metricas["totalProposicoesTrend"] == {
        "value": "+100% vs mês anterior",
        "isPositive": True,
    }
    assert metricas["totalEmTramitacaoTrend"] == {
        "value": "+100% vs mês anterior",
        "isPositive": True,
    }
    assert metricas["proposicoesComAtrasoTrend"] == {
        "value": "+100% vs mês anterior",
        "isPositive": False,
    }
    assert metricas["tempoMedioTramitacaoTrend"] == {
        "value": "+150 dias vs mês anterior",
        "isPositive": False,
    }


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


def test_obter_gargalos(session: Session):
    repo = SQLDashboardRepository(session)
    p1 = ProposicaoModel(
        id="1",
        tipo="PL",
        numero="1",
        ano=2024,
        autor="A",
        status="Em tramitação",
        orgao_atual="CCJ",
        ementa="E1",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        tempo_total_dias=200,
    )
    session.add(p1)
    session.commit()

    gargalos = repo.obter_gargalos(None)
    assert len(gargalos) == 1
    assert gargalos[0]["orgao"] == "CCJ"


def test_obter_proposicoes_para_temas(session: Session):
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
        tempo_total_dias=100,
        tags=["Saúde", "Educação"],
    )
    session.add(p1)
    session.commit()

    temas = repo.obter_proposicoes_para_temas(None)
    assert len(temas) == 1
    assert "Saúde" in temas[0]["tags"]


def test_obter_evolucao_temporal(session: Session):
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
        data_apresentacao="2026-05-15",
        data_ultima_movimentacao="2026-05-15",
        data_encerramento="2026-05-20",
        tempo_total_dias=5,
    )
    session.add(p1)
    session.commit()

    evolucao = repo.obter_evolucao_temporal(None)
    assert len(evolucao) == 7
    mai_data = next((item for item in evolucao if item["mes"] == "Mai/26"), None)
    assert mai_data is not None
    assert mai_data["entradas"] == 1
    assert mai_data["saidas"] == 1


def test_obter_transicoes_casas(session: Session):
    repo = SQLDashboardRepository(session)
    p1 = ProposicaoModel(
        id="1",
        tipo="PL",
        numero="1",
        ano=2024,
        autor="A",
        status="Em tramitação",
        orgao_atual="PLEN",
        orgao_origem="Câmara dos Deputados",
        ementa="E1",
        data_apresentacao="2026-05-01",
        data_ultima_movimentacao="2026-05-10",
    )
    session.add(p1)

    from infrastructure.database.models.evento_tramitacao_model import (
        EventoTramitacaoModel,
    )

    ev1 = EventoTramitacaoModel(
        evento_id=1,
        proposicao_id="1",
        data_evento="2026-05-01",
        sequencia=1,
        sigla_orgao="CD",
        descricao_original="Apresentação",
        tipo_evento="APRESENTACAO",
    )
    ev2 = EventoTramitacaoModel(
        evento_id=2,
        proposicao_id="1",
        data_evento="2026-05-05",
        sequencia=2,
        sigla_orgao="SF",
        descricao_original="Remessa ao Senado",
        tipo_evento="REMESSA_OUTRA_CASA",
    )
    session.add(ev1)
    session.add(ev2)
    session.commit()

    transicoes = repo.obter_transicoes_casas(None)
    assert transicoes["totalCamara"] == 1 or transicoes["totalSenado"] == 1
    transitions = transicoes["transitions"]
    c_s = next(
        t for t in transitions if t["origem"] == "Câmara" and t["destino"] == "Senado"
    )
    assert c_s["quantidade"] == 1
    assert c_s["tempoMedioTransicao"] == 4
