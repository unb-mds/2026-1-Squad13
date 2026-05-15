import pytest
from sqlmodel import Session, SQLModel, create_engine
from domain.entities.tramitacao import Tramitacao
from domain.entities.proposicao import Proposicao
from infrastructure.repositories.sql_tramitacao_repository import (
    SQLTramitacaoRepository,
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Precisamos de uma proposição para a FK
        p = Proposicao(
            id="123",
            tipo="PL",
            numero="1",
            ano=2024,
            autor="Test",
            status="Test",
            ementa="Test",
            data_apresentacao="2024-01-01",
            data_ultima_movimentacao="2024-01-01",
            orgao_atual="Test",
            tags=[],
        )
        session.add(p)
        session.commit()
        yield session


def test_salvar_lote_insere_multiplos(session: Session):
    repo = SQLTramitacaoRepository(session)
    t1 = Tramitacao(
        proposicao_id="123",
        data_hora="2024-01-01T10:00",
        sequencia=1,
        sigla_orgao="OR1",
        descricao_tramitacao="D1",
    )
    t2 = Tramitacao(
        proposicao_id="123",
        data_hora="2024-01-01T11:00",
        sequencia=2,
        sigla_orgao="OR1",
        descricao_tramitacao="D2",
    )

    repo.salvar_lote([t1, t2])

    resultados = repo.buscar_por_proposicao("123")
    assert len(resultados) == 2
    assert resultados[0].sequencia == 2  # Ordenado por seq desc
    assert resultados[1].sequencia == 1


def test_deletar_por_proposicao_limpa_apenas_especifica(session: Session):
    repo = SQLTramitacaoRepository(session)
    # Adiciona para prop 123
    t1 = Tramitacao(
        proposicao_id="123",
        data_hora="2024-01-01T10:00",
        sequencia=1,
        sigla_orgao="OR1",
        descricao_tramitacao="D1",
    )
    session.add(t1)

    # Adiciona para outra prop
    p2 = Proposicao(
        id="456",
        tipo="PL",
        numero="2",
        ano=2024,
        autor="Test",
        status="Test",
        ementa="Test",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        orgao_atual="Test",
        tags=[],
    )
    session.add(p2)
    t2 = Tramitacao(
        proposicao_id="456",
        data_hora="2024-01-01T10:00",
        sequencia=1,
        sigla_orgao="OR1",
        descricao_tramitacao="D1",
    )
    session.add(t2)
    session.commit()

    repo.deletar_por_proposicao("123")

    assert len(repo.buscar_por_proposicao("123")) == 0
    assert len(repo.buscar_por_proposicao("456")) == 1
