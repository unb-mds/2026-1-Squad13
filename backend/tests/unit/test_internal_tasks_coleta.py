"""
Testes unitários para o endpoint POST /internal/tarefas/coleta.

Cobre:
  (a) lock bloqueia execução concorrente → overlap_bloqueado
  (b) asyncio.TimeoutError aciona registrar_fim com status "falha"
  (c) marcar_travadas_como_timeout atualiza registros antigos
"""

import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from infrastructure.database.models.auditoria_coleta_model import AuditoriaColetaModel
from infrastructure.repositories.sql_auditoria_coleta_repository import (
    SQLAuditoriaColetaRepository,
)

# ---------------------------------------------------------------------------
# Fixture de banco in-memory para testes de repositório
# ---------------------------------------------------------------------------


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


# ---------------------------------------------------------------------------
# (c) marcar_travadas_como_timeout
# ---------------------------------------------------------------------------


def test_marcar_travadas_como_timeout_atualiza_registro_antigo(session: Session):
    repo = SQLAuditoriaColetaRepository(session)

    # Insere um registro "executando" com data_inicio de 40 minutos atrás
    registro_antigo = AuditoriaColetaModel(
        job_id="job-travado-001",
        nome_job="coleta_diaria",
        status="executando",
        data_inicio=datetime.now(UTC) - timedelta(minutes=40),
    )
    session.add(registro_antigo)
    session.commit()

    atualizados = repo.marcar_travadas_como_timeout("coleta_diaria", minutos=30)

    assert atualizados == 1
    session.refresh(registro_antigo)
    assert registro_antigo.status == "timeout"
    assert registro_antigo.data_fim is not None
    assert registro_antigo.mensagem_erro is not None


def test_marcar_travadas_nao_toca_registro_recente(session: Session):
    repo = SQLAuditoriaColetaRepository(session)

    # Registro recente: apenas 10 minutos atrás (dentro do limiar de 30 min)
    registro_recente = AuditoriaColetaModel(
        job_id="job-recente-001",
        nome_job="coleta_diaria",
        status="executando",
        data_inicio=datetime.now(UTC) - timedelta(minutes=10),
    )
    session.add(registro_recente)
    session.commit()

    atualizados = repo.marcar_travadas_como_timeout("coleta_diaria", minutos=30)

    assert atualizados == 0
    session.refresh(registro_recente)
    assert registro_recente.status == "executando"


def test_marcar_travadas_nao_toca_outros_jobs(session: Session):
    repo = SQLAuditoriaColetaRepository(session)

    registro_outro_job = AuditoriaColetaModel(
        job_id="job-outro-001",
        nome_job="outro_job",
        status="executando",
        data_inicio=datetime.now(UTC) - timedelta(minutes=60),
    )
    session.add(registro_outro_job)
    session.commit()

    atualizados = repo.marcar_travadas_como_timeout("coleta_diaria", minutos=30)

    assert atualizados == 0
    session.refresh(registro_outro_job)
    assert registro_outro_job.status == "executando"


# ---------------------------------------------------------------------------
# (a) lock bloqueia execução concorrente
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_deps_coleta():
    """
    Monta os patches necessários para isolar o endpoint executar_coleta.
    Retorna um dict com os mocks mais relevantes para asserções.
    """
    resumo_ok = {
        "camara": {"status": "sucesso", "itens_coletados": 5},
        "senado": {"status": "sucesso", "itens_coletados": 3},
    }

    mocks = {}

    with (
        patch(
            "presentation.controllers.internal_tasks_controller.get_redis_client"
        ) as mock_get_redis,
        patch(
            "presentation.controllers.internal_tasks_controller.RedisClient"
        ) as mock_redis_cls,
        patch(
            "presentation.controllers.internal_tasks_controller.SQLAuditoriaColetaRepository"
        ) as mock_auditoria_cls,
        patch(
            "presentation.controllers.internal_tasks_controller.SQLProposicaoRepository"
        ),
        patch(
            "presentation.controllers.internal_tasks_controller.SQLEventoTramitacaoRepository"
        ),
        patch(
            "presentation.controllers.internal_tasks_controller.SQLFaseAnaliticaRepository"
        ),
        patch(
            "presentation.controllers.internal_tasks_controller.SQLOrgaoLegislativoRepository"
        ),
        patch(
            "presentation.controllers.internal_tasks_controller.SQLApensamentoRepository"
        ),
        patch(
            "presentation.controllers.internal_tasks_controller.SQLLogColetaRepository"
        ),
        patch(
            "presentation.controllers.internal_tasks_controller.SQLPeriodoFaseRepository"
        ),
        patch(
            "presentation.controllers.internal_tasks_controller.SQLCoberturaSnapshotRepository"
        ),
        patch("presentation.controllers.internal_tasks_controller.CamaraAdapter"),
        patch("presentation.controllers.internal_tasks_controller.SenadoAdapter"),
        patch(
            "presentation.controllers.internal_tasks_controller.ReconstruirPeriodosService"
        ),
        patch(
            "presentation.controllers.internal_tasks_controller.AtualizarCoberturaService"
        ),
        patch(
            "presentation.controllers.internal_tasks_controller.ColetarEmLoteService"
        ) as mock_service_cls,
    ):
        mock_cache = MagicMock()
        mock_cache.set_nx.return_value = True
        mock_cache.eval_lua.return_value = 1
        mock_redis_cls.return_value = mock_cache
        mock_get_redis.return_value = MagicMock()

        mock_auditoria = MagicMock()
        mock_auditoria.marcar_travadas_como_timeout.return_value = 0
        mock_auditoria_cls.return_value = mock_auditoria

        mock_service = MagicMock()
        mock_service.executar_coleta_diaria = AsyncMock(return_value=resumo_ok)
        mock_service_cls.return_value = mock_service

        mocks["cache"] = mock_cache
        mocks["auditoria"] = mock_auditoria
        mocks["service"] = mock_service
        mocks["resumo_ok"] = resumo_ok

        yield mocks


def _run_endpoint(mock_deps):
    """Executa o endpoint síncrono via asyncio.run com session mockada."""
    from presentation.controllers.internal_tasks_controller import executar_coleta

    mock_session = MagicMock()
    return asyncio.run(executar_coleta(session=mock_session))


def test_lock_bloqueia_execucao_concorrente(mock_deps_coleta):
    """(a) set_nx retorna False → endpoint retorna overlap_bloqueado sem chamar registrar_inicio."""
    mock_deps_coleta["cache"].set_nx.return_value = False

    resultado = _run_endpoint(mock_deps_coleta)

    assert resultado == {"status": "overlap_bloqueado"}
    mock_deps_coleta["auditoria"].registrar_inicio.assert_not_called()
    mock_deps_coleta["service"].executar_coleta_diaria.assert_not_called()


def test_lock_liberado_apos_execucao_normal(mock_deps_coleta):
    """(a) lock adquirido → eval_lua de release deve ser chamado no finally."""
    _run_endpoint(mock_deps_coleta)

    mock_deps_coleta["cache"].eval_lua.assert_called_once()
    args = mock_deps_coleta["cache"].eval_lua.call_args
    assert args[0][1] == ["coleta:lock:coleta_diaria"]


# ---------------------------------------------------------------------------
# (b) timeout interno aciona registrar_fim com status "falha"
# ---------------------------------------------------------------------------


def test_timeout_interno_aciona_registrar_fim_com_falha(mock_deps_coleta):
    """(b) Verifica o bloco except TimeoutError do controller: quando a coroutine levanta
    TimeoutError (como asyncio.wait_for faria ao estourar 240s), registrar_fim deve ser
    chamado com status='falha' e mensagem contendo '240s'. O mecanismo real do wait_for
    (stdlib) não é testado aqui — apenas o tratamento do controller ao receber o erro."""
    mock_deps_coleta["service"].executar_coleta_diaria = AsyncMock(
        side_effect=TimeoutError()
    )

    with pytest.raises(TimeoutError):
        _run_endpoint(mock_deps_coleta)

    mock_deps_coleta["auditoria"].registrar_fim.assert_called_once()
    call_args = mock_deps_coleta["auditoria"].registrar_fim.call_args[0]
    # call_args: (job_id, status, itens, erro)
    assert call_args[1] == "falha"
    assert call_args[2] == 0
    assert "240s" in call_args[3]


def test_timeout_interno_libera_lock(mock_deps_coleta):
    """(b) mesmo com TimeoutError, o lock deve ser liberado no finally."""
    mock_deps_coleta["service"].executar_coleta_diaria = AsyncMock(
        side_effect=TimeoutError()
    )

    with pytest.raises(TimeoutError):
        _run_endpoint(mock_deps_coleta)

    mock_deps_coleta["cache"].eval_lua.assert_called_once()


def test_excecao_generica_aciona_registrar_fim_com_falha(mock_deps_coleta):
    """Fix 1 — qualquer Exception também aciona registrar_fim via finally."""
    mock_deps_coleta["service"].executar_coleta_diaria = AsyncMock(
        side_effect=RuntimeError("erro inesperado")
    )

    with pytest.raises(RuntimeError):
        _run_endpoint(mock_deps_coleta)

    call_args = mock_deps_coleta["auditoria"].registrar_fim.call_args[0]
    assert call_args[1] == "falha"
    assert "erro inesperado" in call_args[3]
