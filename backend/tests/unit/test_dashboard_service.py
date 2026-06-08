import json
from typing import Any

import pytest
from sqlmodel import Session, SQLModel, create_engine

from application.ports.cache_provider import CacheProvider
from application.services.dashboard_service import DashboardService
from domain.entities.proposicao import Proposicao
from infrastructure.repositories.sql_dashboard_repository import SQLDashboardRepository
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)


class MockCacheProvider(CacheProvider):
    def __init__(self):
        self.store = {}

    def get(self, key: str) -> Any | None:
        return self.store.get(key)

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        self.store[key] = value

    def delete(self, key: str) -> None:
        self.store.pop(key, None)

    def invalidate(self, prefix: str) -> None:
        keys_to_delete = [k for k in self.store.keys() if k.startswith(prefix)]
        for k in keys_to_delete:
            self.delete(k)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        repo = SQLProposicaoRepository(session)
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
        repo.salvar(p1)
        repo.salvar(p2)
        yield session


def test_obter_metricas_dashboard_sem_cache(session: Session):
    repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    dashboard_repo = SQLDashboardRepository(session)
    service = DashboardService(repo, evento_repo, dashboard_repo=dashboard_repo)

    metricas = service.obter_metricas()

    assert metricas["totalProposicoes"] == 2
    assert metricas["totalAprovadas"] == 1
    assert metricas["tempoMedioTramitacao"] == 150


def test_obter_metricas_cache_miss_e_set(session: Session):
    repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    dashboard_repo = SQLDashboardRepository(session)
    cache_provider = MockCacheProvider()
    service = DashboardService(
        repo, evento_repo, cache_provider=cache_provider, dashboard_repo=dashboard_repo
    )

    assert cache_provider.get("dashboard:metricas") is None

    # Ocorre o Cache Miss, processa e deve fazer o Set no final
    metricas = service.obter_metricas()

    assert metricas["totalProposicoes"] == 2
    assert metricas["tempoMedioTramitacao"] == 150

    cached_value = cache_provider.get("dashboard:metricas")
    assert cached_value is not None
    # Verifica se os dados salvos em JSON estão corretos
    cached_dict = json.loads(cached_value)
    assert cached_dict["totalProposicoes"] == 2
    assert cached_dict["tempoMedioTramitacao"] == 150


def test_obter_metricas_cache_hit(session: Session):
    repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    cache_provider = MockCacheProvider()
    service = DashboardService(repo, evento_repo, cache_provider=cache_provider)

    # Simula um Cache Hit
    mock_data = {
        "tempoMedioTramitacao": 500,
        "totalProposicoes": 10,
        "proposicoesComAtraso": 5,
        "totalAprovadas": 2,
        "totalEmTramitacao": 3,
        "totalRejeitadas": 5,
        "comissaoMaiorTempo": "MOCK",
        "comissaoMaiorTempoMedia": 1000,
    }
    cache_provider.set("dashboard:metricas", json.dumps(mock_data))

    # Deve retornar o cache e não processar nada (mesmo sem dashboard_repo)
    metricas = service.obter_metricas()

    assert metricas["totalProposicoes"] == 10
    assert metricas["tempoMedioTramitacao"] == 500
    assert metricas["comissaoMaiorTempo"] == "MOCK"


def test_obter_cobertura_dados_sem_cache(session: Session):
    repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    dashboard_repo = SQLDashboardRepository(session)
    service = DashboardService(repo, evento_repo, dashboard_repo=dashboard_repo)

    cobertura = service.obter_cobertura_dados()
    # Ambos os registros P1 e P2 têm ementa, autor, etc. mas sem link_oficial.
    # Vamos verificar que o repositório foi chamado e retornou as métricas de cobertura.
    assert "eventosDocumentados" in cobertura
    assert "metadadosCompletos" in cobertura
    assert "historicoTramitacao" in cobertura
    assert "documentosAnexos" in cobertura
    assert "coberturaConsolidada" in cobertura


def test_obter_cobertura_dados_cache_miss_e_set(session: Session):
    repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    dashboard_repo = SQLDashboardRepository(session)
    cache_provider = MockCacheProvider()
    service = DashboardService(
        repo,
        evento_repo,
        cache_provider=cache_provider,
        dashboard_repo=dashboard_repo,
    )

    assert cache_provider.get("dashboard:cobertura_dados") is None

    cobertura = service.obter_cobertura_dados()
    assert "eventosDocumentados" in cobertura

    cached_value = cache_provider.get("dashboard:cobertura_dados")
    assert cached_value is not None
    cached_dict = json.loads(cached_value)
    assert "eventosDocumentados" in cached_dict


def test_obter_cobertura_dados_cache_hit(session: Session):
    repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    cache_provider = MockCacheProvider()
    service = DashboardService(repo, evento_repo, cache_provider=cache_provider)

    mock_data = {
        "eventosDocumentados": 99.9,
        "metadadosCompletos": 88.8,
        "historicoTramitacao": 77.7,
        "documentosAnexos": 66.6,
        "coberturaConsolidada": 83.2,
    }
    cache_provider.set("dashboard:cobertura_dados", json.dumps(mock_data))

    cobertura = service.obter_cobertura_dados()

    assert cobertura["eventosDocumentados"] == 99.9
    assert cobertura["metadadosCompletos"] == 88.8
    assert cobertura["coberturaConsolidada"] == 83.2

