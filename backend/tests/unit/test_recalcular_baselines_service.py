from unittest.mock import MagicMock

import pytest
from sqlmodel import Session, SQLModel, create_engine

from application.services.recalcular_baselines_service import RecalcularBaselinesService
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.fase_analitica import FASES_SEED
from domain.entities.proposicao import Proposicao
from infrastructure.database.models.fase_analitica_model import FaseAnaliticaModel
from infrastructure.repositories.sql_baseline_tramitacao_repository import (
    SQLBaselineTramitacaoRepository,
)
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Cadastra as fases de seed
        for f in FASES_SEED:
            session.add(FaseAnaliticaModel(**f))
        session.commit()
        yield session

    engine.dispose()


def test_recalcular_baselines_sem_massa_suficiente(session: Session):
    # Arrange
    prop_repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    fase_repo = SQLFaseAnaliticaRepository(session)
    baseline_repo = SQLBaselineTramitacaoRepository(session)

    # Adiciona apenas 5 proposições concluídas
    for i in range(5):
        pid = f"PL-{i}-2026"
        prop = Proposicao(
            id=pid,
            tipo="PL",
            numero=str(i),
            ano=2026,
            ementa="Ementa teste",
            autor="Autor",
            status="Sancionada",
            orgao_atual="Plenário",
            data_apresentacao="2026-05-01",
            data_ultima_movimentacao="2026-05-11",
            data_encerramento="2026-05-11",
            regime_tramitacao="ORDINARIO",
            tags=[],
        )
        prop_repo.salvar(prop)
        evento_repo.salvar(
            EventoTramitacao(
                proposicao_id=pid,
                data_evento="2026-05-01",
                sequencia=1,
                tipo_evento="APRESENTACAO",
                descricao_original="Apresentação",
            )
        )
        evento_repo.salvar(
            EventoTramitacao(
                proposicao_id=pid,
                data_evento="2026-05-11",
                sequencia=2,
                tipo_evento="PROMULGACAO",
                descricao_original="Promulgação",
            )
        )

    # Act
    service = RecalcularBaselinesService(
        prop_repo, evento_repo, fase_repo, baseline_repo
    )
    resultado = service.executar()

    # Assert - Não deve ter criado nenhum baseline dinâmico porque n < 30
    assert resultado["total_iar_criados"] == 0
    assert resultado["total_iaf_criados"] == 0


def test_recalcular_baselines_com_massa_suficiente(session: Session):
    # Arrange
    prop_repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    fase_repo = SQLFaseAnaliticaRepository(session)
    baseline_repo = SQLBaselineTramitacaoRepository(session)

    # Adiciona 30 proposições concluídas com duração de 10 dias cada
    for i in range(30):
        pid = f"PL-{i}-2026"
        prop = Proposicao(
            id=pid,
            tipo="PL",
            numero=str(i),
            ano=2026,
            ementa="Ementa teste",
            autor="Autor",
            status="Sancionada",
            orgao_atual="Plenário",
            data_apresentacao="2026-05-01",
            data_ultima_movimentacao="2026-05-11",
            data_encerramento="2026-05-11",
            regime_tramitacao="ORDINARIO",
            tags=[],
        )
        prop_repo.salvar(prop)
        # Eventos para IAR e IAF
        evento_repo.salvar(
            EventoTramitacao(
                proposicao_id=pid,
                data_evento="2026-05-01",
                sequencia=1,
                tipo_evento="APRESENTACAO",
                descricao_original="Apresentação",
                fase_analitica_id=1,  # PROTOCOLO_INICIAL
            )
        )
        evento_repo.salvar(
            EventoTramitacao(
                proposicao_id=pid,
                data_evento="2026-05-11",
                sequencia=2,
                tipo_evento="PROMULGACAO",
                descricao_original="Promulgação",
            )
        )

    # Act
    service = RecalcularBaselinesService(
        prop_repo, evento_repo, fase_repo, baseline_repo
    )
    resultado = service.executar()

    # Assert - Deve criar baseline dinâmico para TOTAL (n >= 30) e para Fase PROTOCOLO_INICIAL (n >= 30)
    assert resultado["total_iar_criados"] == 1
    assert resultado["total_iaf_criados"] == 1

    baseline_total = baseline_repo.buscar_baseline(
        escopo="TOTAL", tipo="PL", regime_tramitacao="ORDINARIO"
    )
    assert baseline_total is not None
    assert baseline_total.mediana_dias == 10  # 11 - 1
    assert baseline_total.origem_dados == "DYNAMIC_CALCULATION"

    baseline_fase = baseline_repo.buscar_baseline(
        escopo="FASE",
        tipo="PL",
        regime_tramitacao="ORDINARIO",
        fase_codigo="PROTOCOLO_INICIAL",
    )
    assert baseline_fase is not None
    assert baseline_fase.mediana_dias == 10
    assert baseline_fase.origem_dados == "DYNAMIC_CALCULATION"


def test_calcular_mediana():
    assert RecalcularBaselinesService.calcular_mediana([]) == 0
    assert RecalcularBaselinesService.calcular_mediana([5]) == 5
    assert RecalcularBaselinesService.calcular_mediana([1, 10, 5]) == 5
    assert (
        RecalcularBaselinesService.calcular_mediana([1, 2, 3, 4]) == 3
    )  # (2+3)/2 = 2.5 rounded is 3


def test_recalcular_baselines_error(session):
    # Mock de um dos repositórios para subir erro
    mock_repo = MagicMock()
    mock_repo.filtrar.side_effect = Exception("Erro DB")

    service = RecalcularBaselinesService(
        proposicao_repo=mock_repo,
        evento_repo=MagicMock(),
        fase_repo=MagicMock(),
        baseline_repo=MagicMock(),
    )

    with pytest.raises(Exception) as exc:
        service.executar()
    assert "Erro DB" in str(exc.value)
