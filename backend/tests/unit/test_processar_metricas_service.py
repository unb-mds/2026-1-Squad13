from datetime import date, timedelta

import pytest
from sqlmodel import Session, SQLModel, create_engine

from application.services.processar_metricas_service import ProcessarMetricasService
from domain.entities.baseline_tramitacao import BaselineTramitacao
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


def test_processar_metricas_fluxo_completo(session: Session):
    # Arrange
    prop_repo = SQLProposicaoRepository(session)
    evento_repo = SQLEventoTramitacaoRepository(session)
    fase_repo = SQLFaseAnaliticaRepository(session)
    baseline_repo = SQLBaselineTramitacaoRepository(session)

    # 1. Cadastra baselines
    baseline_repo.salvar(
        BaselineTramitacao(
            escopo="TOTAL",
            tipo="PL",
            regime_tramitacao="ORDINARIO",
            mediana_dias=100,
            origem_dados="BOOTSTRAP_SEED",
        )
    )
    baseline_repo.salvar(
        BaselineTramitacao(
            escopo="FASE",
            tipo="PL",
            regime_tramitacao="ORDINARIO",
            fase_codigo="ANALISE_COMISSOES",
            mediana_dias=20,
            origem_dados="BOOTSTRAP_SEED",
        )
    )

    # 2. Cadastra proposição apresentada há 10 dias
    data_apresentacao = (date.today() - timedelta(days=10)).isoformat()
    prop = Proposicao(
        id="PL-999-2026",
        tipo="PL",
        numero="999",
        ano=2026,
        ementa="Ementa teste",
        autor="Autor",
        status="Em comissões",
        orgao_atual="CCJ",
        data_apresentacao=data_apresentacao,
        data_ultima_movimentacao=data_apresentacao,
        regime_tramitacao="ORDINARIO",
        tags=[],
    )
    prop_repo.salvar(prop)

    # 3. Cadastra eventos
    fases = fase_repo.buscar_todas()
    fase_comissoes_id = [f.id for f in fases if f.codigo == "ANALISE_COMISSOES"][0]

    evento_repo.salvar(
        EventoTramitacao(
            proposicao_id="PL-999-2026",
            data_evento=data_apresentacao,
            sequencia=1,
            tipo_evento="APRESENTACAO",
            descricao_original="Apresentação do projeto",
            fase_analitica_id=1,
            deliberativo=False,
            mudou_fase=False,
            mudou_orgao=False,
            dias_na_etapa=4,
        )
    )
    # Entrou em comissões há 6 dias
    data_comissoes = (date.today() - timedelta(days=6)).isoformat()
    evento_repo.salvar(
        EventoTramitacao(
            proposicao_id="PL-999-2026",
            data_evento=data_comissoes,
            sequencia=2,
            tipo_evento="RECEBIMENTO_ORGAO",
            descricao_original="Recebido na CCJ",
            fase_analitica_id=fase_comissoes_id,
            deliberativo=False,
            mudou_fase=True,
            mudou_orgao=False,
            dias_na_etapa=6,
        )
    )

    # Act
    service = ProcessarMetricasService(prop_repo, evento_repo, fase_repo, baseline_repo)
    resultado = service.executar(["PL-999-2026"])

    # Assert
    assert resultado["sucessos"] == 1

    prop_atualizada = prop_repo.buscar_por_id("PL-999-2026")
    assert prop_atualizada is not None
    assert prop_atualizada.dias_decorridos_total == 10
    # IAR: 10 / 100 = 0.1
    assert prop_atualizada.indice_atraso_relativo == 0.1
    assert prop_atualizada.status_atraso == "NO_PRAZO"
    # IEI: Evento 1 é improdutivo (4 dias). IEI = 4 / 10 = 0.4
    assert prop_atualizada.indice_espera_improdutiva == 0.4
    # IAF: 6 dias na fase de comissões. Baseline da fase é 20. IAF = 6 / 20 = 0.3
    assert prop_atualizada.indice_atraso_fase_atual == 0.3
