import pytest
from sqlmodel import Session, SQLModel, create_engine
from domain.entities.proposicao import Proposicao
from infrastructure.repositories.sql_proposicao_repository import SQLProposicaoRepository

@pytest.fixture(name="session")
def session_fixture():
    """Cria um banco de dados em memória para cada teste."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_salvar_proposicao(session: Session):
    # Arrange (Organizar)
    repo = SQLProposicaoRepository(session)
    nova_prop = Proposicao(
        id="10",
        tipo="PL",
        numero="999",
        ano=2026,
        autor="Dev Test",
        uf_autor="BR",
        status="Novo",
        orgao_atual="Mesa",
        ementa="Teste de persistência",
        data_apresentacao="2026-01-01",
        data_ultima_movimentacao="2026-01-01",
        tags=["teste"]
    )

    # Act (Agir)
    repo.salvar(nova_prop)

    # Assert (Verificar)
    buscada = repo.buscar_por_id("10")
    assert buscada is not None
    assert buscada.numero == "999"
    assert buscada.autor == "Dev Test"
