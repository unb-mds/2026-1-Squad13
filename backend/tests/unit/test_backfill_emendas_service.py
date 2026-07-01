from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlmodel import Session, SQLModel, create_engine

from application.services.backfill_emendas_service import BackfillEmendasService
from domain.entities.proposicao import Proposicao
from infrastructure.database.models.proposicao_model import ProposicaoModel


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def mock_camara_adapter():
    return MagicMock()


@pytest.fixture
def mock_senado_adapter():
    return MagicMock()


@pytest.fixture
def service(session, mock_camara_adapter, mock_senado_adapter):
    return BackfillEmendasService(
        session=session,
        camara_adapter=mock_camara_adapter,
        senado_adapter=mock_senado_adapter,
    )


@pytest.mark.asyncio
async def test_backfill_emendas_no_pending_propositions(service):
    res = await service.executar()
    assert res == {"atualizadas": 0, "falhas": 0}


@pytest.mark.asyncio
async def test_backfill_emendas_success_camara_and_senado(
    session, service, mock_camara_adapter, mock_senado_adapter
):
    # Proposição da Câmara que necessita de backfill (numero_emendas é None)
    camara_prop = ProposicaoModel(
        id="camara:200",
        tipo="PL",
        numero="200",
        ano=2023,
        ementa="Ementa camara",
        autor="Autor Ficticio",
        status="Em tramitação",
        orgao_atual="CCJ",
        data_apresentacao="2023-01-01",
        data_ultima_movimentacao="2023-01-02",
        orgao_origem="Câmara dos Deputados",
        numero_emendas=None,
    )
    # Proposição do Senado que necessita de backfill (numero_emendas é None)
    senado_prop = ProposicaoModel(
        id="senado:300",
        tipo="PLS",
        numero="300",
        ano=2023,
        ementa="Ementa senado",
        autor="Autor Ficticio",
        status="Em tramitação",
        orgao_atual="CCJ",
        data_apresentacao="2023-01-01",
        data_ultima_movimentacao="2023-01-02",
        orgao_origem="Senado Federal",
        numero_emendas=None,
    )
    session.add(camara_prop)
    session.add(senado_prop)
    session.commit()

    # Configura mocks para retornar proposições atualizadas
    updated_camara = Proposicao(
        id="camara:200",
        tipo="PL",
        numero="200",
        ano=2023,
        ementa="Ementa camara",
        autor="Autor",
        status="Status",
        orgao_origem="Câmara dos Deputados",
        numero_emendas=5,
    )
    updated_senado = Proposicao(
        id="senado:300",
        tipo="PLS",
        numero="300",
        ano=2023,
        ementa="Ementa senado",
        autor="Autor",
        status="Status",
        orgao_origem="Senado Federal",
        numero_emendas=10,
    )

    mock_camara_adapter.buscar_por_id = AsyncMock(return_value=updated_camara)
    mock_senado_adapter.buscar_por_id = AsyncMock(return_value=updated_senado)

    res = await service.executar()
    assert res == {"atualizadas": 2, "falhas": 0}

    # Verifica se as alterações foram salvas no banco
    session.expire_all()
    camara_db = session.get(ProposicaoModel, "camara:200")
    senado_db = session.get(ProposicaoModel, "senado:300")
    assert camara_db.numero_emendas == 5
    assert senado_db.numero_emendas == 10


@pytest.mark.asyncio
async def test_backfill_emendas_with_exception_in_adapter(
    session, service, mock_camara_adapter
):
    camara_prop = ProposicaoModel(
        id="camara:400",
        tipo="PL",
        numero="400",
        ano=2023,
        ementa="Ementa erro",
        autor="Autor Ficticio",
        status="Em tramitação",
        orgao_atual="CCJ",
        data_apresentacao="2023-01-01",
        data_ultima_movimentacao="2023-01-02",
        orgao_origem="Câmara dos Deputados",
        numero_emendas=None,
    )
    session.add(camara_prop)
    session.commit()

    # Configura mock do adapter para levantar exceção
    mock_camara_adapter.buscar_por_id = AsyncMock(
        side_effect=Exception("Erro de conexão na API")
    )

    res = await service.executar()
    assert res == {"atualizadas": 0, "falhas": 1}

    # Verifica que o número de emendas no banco permanece None
    session.expire_all()
    camara_db = session.get(ProposicaoModel, "camara:400")
    assert camara_db.numero_emendas is None


@pytest.mark.asyncio
async def test_backfill_emendas_adapter_returns_none(
    session, service, mock_camara_adapter
):
    camara_prop = ProposicaoModel(
        id="camara:500",
        tipo="PL",
        numero="500",
        ano=2023,
        ementa="Ementa nula",
        autor="Autor Ficticio",
        status="Em tramitação",
        orgao_atual="CCJ",
        data_apresentacao="2023-01-01",
        data_ultima_movimentacao="2023-01-02",
        orgao_origem="Câmara dos Deputados",
        numero_emendas=None,
    )
    session.add(camara_prop)
    session.commit()

    mock_camara_adapter.buscar_por_id = AsyncMock(return_value=None)

    res = await service.executar()
    assert res == {"atualizadas": 0, "falhas": 0}

    # Verifica que o número de emendas no banco permanece None
    session.expire_all()
    camara_db = session.get(ProposicaoModel, "camara:500")
    assert camara_db.numero_emendas is None
