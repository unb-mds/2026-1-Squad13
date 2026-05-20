import pytest
from sqlmodel import Session, create_engine, SQLModel
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)
from infrastructure.database.models.proposicao_model import ProposicaoModel
from domain.entities.proposicao import Proposicao


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_upsert_em_lote_idempotencia(session):
    repo = SQLProposicaoRepository(session)

    prop1 = Proposicao(
        id="1",
        tipo="PL",
        numero="100",
        ano=2024,
        autor="Autor A",
        ementa="Ementa A",
        data_apresentacao="2024-01-01",
        orgao_origem="Câmara",
        status="Ativo",
        orgao_atual="Câmara",
        link_oficial="link",
        data_ultima_movimentacao="2024-01-01",
    )

    # 1. Primeiro insert
    repo.upsert_em_lote_por_numero_canonico([prop1])

    saved = repo.buscar_por_codigo("PL", "100", 2024)
    assert saved is not None
    assert saved.autor == "Autor A"

    # 2. Update via upsert (mesma chave canônica, autor diferente)
    prop1_mod = prop1.model_copy(update={"autor": "Autor B", "ementa": "Ementa B"})
    repo.upsert_em_lote_por_numero_canonico([prop1_mod])

    session.expire_all()
    updated = repo.buscar_por_codigo("PL", "100", 2024)
    assert updated.autor == "Autor B"
    assert updated.ementa == "Ementa B"
    assert updated.id == saved.id  # ID deve ser mantido


def test_upsert_em_lote_multiplos(session):
    repo = SQLProposicaoRepository(session)

    props = [
        Proposicao(
            id="1",
            tipo="PL",
            numero="101",
            ano=2024,
            autor="A1",
            ementa="E1",
            data_apresentacao="2024-01-01",
            orgao_origem="C",
            status="S",
            orgao_atual="O",
            link_oficial="L",
            data_ultima_movimentacao="D",
        ),
        Proposicao(
            id="2",
            tipo="PEC",
            numero="1",
            ano=2024,
            autor="A2",
            ementa="E2",
            data_apresentacao="2024-01-01",
            orgao_origem="S",
            status="S",
            orgao_atual="O",
            link_oficial="L",
            data_ultima_movimentacao="D",
        ),
    ]

    repo.upsert_em_lote_por_numero_canonico(props)

    assert session.query(ProposicaoModel).count() == 2
    assert repo.buscar_por_codigo("PL", "101", 2024) is not None
    assert repo.buscar_por_codigo("PEC", "1", 2024) is not None


def test_upsert_em_lote_case_insensitivity(session):
    repo = SQLProposicaoRepository(session)

    prop = Proposicao(
        id="1",
        tipo="pl",
        numero="200",
        ano=2024,
        autor="A",
        ementa="E",
        data_apresentacao="2024-01-01",
        orgao_origem="C",
        status="S",
        orgao_atual="O",
        link_oficial="L",
        data_ultima_movimentacao="D",
    )
    repo.upsert_em_lote_por_numero_canonico([prop])

    # Busca com CAPS diferente deve funcionar tanto no repo quanto no upsert interno
    prop_caps = prop.model_copy(update={"tipo": "PL", "autor": "Novo Autor"})
    repo.upsert_em_lote_por_numero_canonico([prop_caps])

    session.expire_all()
    saved = repo.buscar_por_codigo("pL", "200", 2024)
    assert saved.autor == "Novo Autor"
    assert session.query(ProposicaoModel).count() == 1
