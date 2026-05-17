import pytest
import json
from sqlmodel import Session, SQLModel, create_engine
from typing import Any, Optional

from domain.entities.proposicao import Proposicao
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from application.services.dashboard_service import DashboardService
from application.ports.cache_provider import CacheProvider


class MockCacheProvider(CacheProvider):
    def __init__(self):
        self.store = {}
    
    def get(self, key: str) -> Optional[Any]:
        return self.store.get(key)
        
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
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


def test_obter_metricas_dashboard_sem_cache(session: Session):
    repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    service = DashboardService(repo, evento_repo)

    metricas = service.obter_metricas()

    assert metricas["totalProposicoes"] == 2
    assert metricas["totalAprovadas"] == 1
    assert metricas["tempoMedioTramitacao"] == 150


def test_obter_metricas_cache_miss_e_set(session: Session):
    repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    cache_provider = MockCacheProvider()
    service = DashboardService(repo, evento_repo, cache_provider=cache_provider)

    assert cache_provider.get("dashboard:metricas") is None

    # Ocorre o Cache Miss, processa e deve fazer o Set no final
    metricas = service.obter_metricas()
    
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

    dados_simulados = {
        "tempoMedioTramitacao": 999,
        "totalProposicoes": 50,
        "proposicoesComAtraso": 10,
        "totalAprovadas": 20,
        "totalEmTramitacao": 20,
        "totalRejeitadas": 10,
        "comissaoMaiorTempo": "MOCK",
        "comissaoMaiorTempoMedia": 999
    }
    
    cache_provider.set("dashboard:metricas", json.dumps(dados_simulados))
    
    # Deve pegar direto do cache (Cache Hit) e não processar os dados do banco
    metricas = service.obter_metricas()
    
    assert metricas["totalProposicoes"] == 50
    assert metricas["tempoMedioTramitacao"] == 999
    assert metricas["comissaoMaiorTempo"] == "MOCK"

def test_cache_provider_invalidation():
    cache_provider = MockCacheProvider()
    cache_provider.set("dashboard:metricas", '{"a": 1}')
    cache_provider.set("dashboard:tipos", '{"b": 2}')
    cache_provider.set("outra:chave", "valor")
    
    # Invalida tudo do dashboard
    cache_provider.invalidate("dashboard:")
    
    assert cache_provider.get("dashboard:metricas") is None
    assert cache_provider.get("dashboard:tipos") is None
    assert cache_provider.get("outra:chave") == "valor"
