import pytest
from sqlmodel import Session, SQLModel, create_engine

from domain.entities.baseline_tramitacao import BaselineTramitacao
from infrastructure.repositories.sql_baseline_tramitacao_repository import (
    SQLBaselineTramitacaoRepository,
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

    engine.dispose()


def test_salvar_e_buscar_baseline_exato(session: Session):
    # Arrange
    repo = SQLBaselineTramitacaoRepository(session)
    baseline = BaselineTramitacao(
        escopo="TOTAL",
        tipo="PL",
        regime_tramitacao="ORDINARIO",
        fase_codigo=None,
        mediana_dias=730,
        origem_dados="BOOTSTRAP_SEED",
    )

    # Act
    repo.salvar(baseline)

    # Assert
    buscado = repo.buscar_baseline(
        escopo="TOTAL", tipo="PL", regime_tramitacao="ORDINARIO"
    )
    assert buscado is not None
    assert buscado.mediana_dias == 730
    assert buscado.origem_dados == "BOOTSTRAP_SEED"


def test_buscar_baseline_fallback_regime_nulo(session: Session):
    # Arrange
    repo = SQLBaselineTramitacaoRepository(session)
    # Salva baseline com regime nulo
    baseline = BaselineTramitacao(
        escopo="TOTAL",
        tipo="PL",
        regime_tramitacao=None,
        fase_codigo=None,
        mediana_dias=500,
        origem_dados="BOOTSTRAP_SEED",
    )
    repo.salvar(baseline)

    # Act - Busca informando um regime que não tem cadastro exato
    buscado = repo.buscar_baseline(
        escopo="TOTAL", tipo="PL", regime_tramitacao="URGENCIA"
    )

    # Assert - Deve retornar o baseline com regime_tramitacao = None
    assert buscado is not None
    assert buscado.mediana_dias == 500


def test_buscar_baseline_fallback_global_fase(session: Session):
    # Arrange
    repo = SQLBaselineTramitacaoRepository(session)
    # Salva baseline global de fase (tipo e regime nulos)
    baseline = BaselineTramitacao(
        escopo="FASE",
        tipo=None,
        regime_tramitacao=None,
        fase_codigo="PROTOCOLO_INICIAL",
        mediana_dias=15,
        origem_dados="BOOTSTRAP_SEED",
    )
    repo.salvar(baseline)

    # Act - Busca informando Tipo e Regime específicos
    buscado = repo.buscar_baseline(
        escopo="FASE",
        tipo="PEC",
        regime_tramitacao="ORDINARIO",
        fase_codigo="PROTOCOLO_INICIAL",
    )

    # Assert - Deve cair no fallback global daquela fase
    assert buscado is not None
    assert buscado.mediana_dias == 15


def test_salvar_upsert_evita_duplicados(session: Session):
    # Arrange
    repo = SQLBaselineTramitacaoRepository(session)
    b1 = BaselineTramitacao(
        escopo="TOTAL",
        tipo="PL",
        regime_tramitacao="URGENCIA",
        mediana_dias=90,
        origem_dados="BOOTSTRAP_SEED",
    )
    repo.salvar(b1)

    # Act - Salva mesma combinação alterando mediana e origem
    b2 = BaselineTramitacao(
        escopo="TOTAL",
        tipo="PL",
        regime_tramitacao="URGENCIA",
        mediana_dias=95,
        origem_dados="DYNAMIC_CALCULATION",
    )
    repo.salvar(b2)

    # Assert
    buscado = repo.buscar_baseline(
        escopo="TOTAL", tipo="PL", regime_tramitacao="URGENCIA"
    )
    assert buscado is not None
    assert buscado.mediana_dias == 95
    assert buscado.origem_dados == "DYNAMIC_CALCULATION"


def test_remover_calculos_dinamicos(session: Session):
    # Arrange
    repo = SQLBaselineTramitacaoRepository(session)
    b_seed = BaselineTramitacao(
        escopo="TOTAL",
        tipo="PL",
        regime_tramitacao="ORDINARIO",
        mediana_dias=730,
        origem_dados="BOOTSTRAP_SEED",
    )
    b_dyn = BaselineTramitacao(
        escopo="TOTAL",
        tipo="PEC",
        regime_tramitacao="ORDINARIO",
        mediana_dias=1000,
        origem_dados="DYNAMIC_CALCULATION",
    )
    repo.salvar(b_seed)
    repo.salvar(b_dyn)

    # Act
    repo.remover_calculos_dinamicos()

    # Assert
    assert repo.buscar_baseline("TOTAL", "PL", "ORDINARIO") is not None
    assert repo.buscar_baseline("TOTAL", "PEC", "ORDINARIO") is None
