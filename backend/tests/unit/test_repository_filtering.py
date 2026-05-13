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

def test_filtrar_por_busca_case_insensitive(session: Session):
    repo = SQLProposicaoRepository(session)
    resultados = repo.filtrar(busca="projeto de teste 2")
    assert len(resultados) == 1
    assert resultados[0].id == "2"

def test_atraso_critico_property(session: Session):
    p = Proposicao(tipo="PL", numero="1", ano=2024, autor="A", status="S", orgao_atual="O", ementa="E",
                   data_apresentacao="D", data_ultima_movimentacao="D", tempo_total_dias=200)
    assert p.atraso_critico is True

    p.tempo_total_dias = 180
    assert p.atraso_critico is False

def test_filtrar_com_limit_retorna_apenas_n_registros(session: Session):
    repo = SQLProposicaoRepository(session)
    resultados = repo.filtrar(limit=1)
    assert len(resultados) == 1

def test_filtrar_com_offset_pula_registros(session: Session):
    repo = SQLProposicaoRepository(session)
    todos = repo.filtrar()
    com_offset = repo.filtrar(offset=1)
    assert len(com_offset) == len(todos) - 1

def test_filtrar_limit_e_offset_combinados(session: Session):
    repo = SQLProposicaoRepository(session)
    primeira_pagina = repo.filtrar(limit=1, offset=0)
    segunda_pagina = repo.filtrar(limit=1, offset=1)
    assert len(primeira_pagina) == 1
    assert len(segunda_pagina) == 1
    assert primeira_pagina[0].id != segunda_pagina[0].id

def test_contar_retorna_total_sem_paginacao(session: Session):
    repo = SQLProposicaoRepository(session)
    total = repo.contar()
    assert total == 2

def test_contar_com_filtro_status(session: Session):
    repo = SQLProposicaoRepository(session)
    total = repo.contar(status="Aprovada")
    assert total == 1

def test_contar_sem_resultados(session: Session):
    repo = SQLProposicaoRepository(session)
    total = repo.contar(status="Inexistente")
    assert total == 0
