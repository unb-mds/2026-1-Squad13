import pytest
from sqlmodel import Session, SQLModel, create_engine
from domain.entities.proposicao import Proposicao
from infrastructure.repositories.sql_proposicao_repository import SQLProposicaoRepository

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Adicionar dados de teste
        p1 = Proposicao(
            id="1", tipo="PL", numero="1", ano=2024, autor="Autor A", 
            status="Aprovada", orgao_atual="Câmara", ementa="Projeto de teste 1",
            data_apresentacao="2024-01-01", data_ultima_movimentacao="2024-01-01",
            orgao_origem="Câmara"
        )
        p2 = Proposicao(
            id="2", tipo="PEC", numero="2", ano=2024, autor="Autor B", 
            status="Em tramitação", orgao_atual="Senado", ementa="Projeto de teste 2",
            data_apresentacao="2024-02-01", data_ultima_movimentacao="2024-02-01",
            orgao_origem="Senado"
        )
        session.add(p1)
        session.add(p2)
        session.commit()
        yield session

def test_filtrar_por_status(session: Session):
    repo = SQLProposicaoRepository(session)
    resultados = repo.filtrar(status="Aprovada")
    assert len(resultados) == 1
    assert resultados[0].id == "1"

def test_filtrar_por_busca_texto(session: Session):
    repo = SQLProposicaoRepository(session)
    # Busca por ementa
    resultados = repo.filtrar(busca="Projeto de teste 2")
    assert len(resultados) == 1
    assert resultados[0].id == "2"

def test_filtrar_por_data_range(session: Session):
    repo = SQLProposicaoRepository(session)
    resultados = repo.filtrar(data_inicio="2024-01-15")
    assert len(resultados) == 1
    assert resultados[0].id == "2"

def test_atraso_critico_property(session: Session):
    p = Proposicao(tipo="PL", numero="1", ano=2024, autor="A", status="S", orgao_atual="O", ementa="E", 
                   data_apresentacao="D", data_ultima_movimentacao="D", tempo_total_dias=200)
    assert p.atraso_critico is True
    
    p.tempo_total_dias = 180
    assert p.atraso_critico is False
