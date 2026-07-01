from datetime import date

import pytest
from sqlmodel import Session, SQLModel, create_engine

from domain.entities.periodo_fase import PeriodoFase
from infrastructure.repositories.sql_periodo_fase_repository import (
    SQLPeriodoFaseRepository,
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def repository(session):
    return SQLPeriodoFaseRepository(session)


def test_salvar_lote_vazio(repository):
    res = repository.salvar_lote([])
    assert res == []


def test_salvar_lote_e_buscar_por_proposicao(session, repository):
    p1 = PeriodoFase(
        id=None,
        proposicao_id="prop:1",
        fase_analitica_id=1,
        data_inicio=date(2023, 1, 1),
        data_fim=date(2023, 1, 10),
        duracao_dias=9,
        recorrencia_numero=1,
        eh_fase_atual=False,
        tipo_proposicao="PL",
        rito="Ordinário",
        origem_calculo="API",
    )
    p2 = PeriodoFase(
        id=None,
        proposicao_id="prop:1",
        fase_analitica_id=2,
        data_inicio=date(2023, 1, 11),
        data_fim=None,
        duracao_dias=None,
        recorrencia_numero=1,
        eh_fase_atual=True,
        tipo_proposicao="PL",
        rito="Ordinário",
        origem_calculo="API",
    )
    # Proposição diferente
    p_outra = PeriodoFase(
        id=None,
        proposicao_id="prop:2",
        fase_analitica_id=1,
        data_inicio=date(2023, 1, 5),
        data_fim=None,
        duracao_dias=None,
        recorrencia_numero=1,
        eh_fase_atual=True,
        tipo_proposicao="PL",
        rito="Ordinário",
        origem_calculo="API",
    )

    res = repository.salvar_lote([p1, p2, p_outra])
    assert len(res) == 3

    # Busca períodos da prop:1
    periodos_prop1 = repository.buscar_por_proposicao("prop:1")
    assert len(periodos_prop1) == 2
    # Verifica a ordenação
    assert periodos_prop1[0].fase_analitica_id == 1
    assert periodos_prop1[0].data_inicio == date(2023, 1, 1)
    assert periodos_prop1[1].fase_analitica_id == 2
    assert periodos_prop1[1].data_inicio == date(2023, 1, 11)


def test_deletar_por_proposicao(session, repository):
    p1 = PeriodoFase(
        id=None,
        proposicao_id="prop:3",
        fase_analitica_id=1,
        data_inicio=date(2023, 1, 1),
        data_fim=None,
        duracao_dias=None,
        recorrencia_numero=1,
        eh_fase_atual=True,
        tipo_proposicao="PL",
        rito="Ordinário",
        origem_calculo="API",
    )
    p_outra = PeriodoFase(
        id=None,
        proposicao_id="prop:4",
        fase_analitica_id=1,
        data_inicio=date(2023, 1, 5),
        data_fim=None,
        duracao_dias=None,
        recorrencia_numero=1,
        eh_fase_atual=True,
        tipo_proposicao="PL",
        rito="Ordinário",
        origem_calculo="API",
    )
    repository.salvar_lote([p1, p_outra])

    # Deleta prop:3
    repository.deletar_por_proposicao("prop:3")

    # Verifica que prop:3 foi apagada e prop:4 continua ativa
    res_prop3 = repository.buscar_por_proposicao("prop:3")
    res_prop4 = repository.buscar_por_proposicao("prop:4")
    assert len(res_prop3) == 0
    assert len(res_prop4) == 1
