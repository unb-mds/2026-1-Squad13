from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from application.services.reconstruir_periodos_service import ReconstruirPeriodosService
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.fase_analitica import FaseAnalitica
from domain.entities.proposicao import Proposicao


@pytest.fixture
def mock_fases():
    return [
        FaseAnalitica(
            id=1, codigo="PROTOCOLO_INICIAL", nome="Protocolo", ordem_logica=1
        ),
        FaseAnalitica(
            id=2, codigo="ANALISE_COMISSOES", nome="Comissões", ordem_logica=2
        ),
        FaseAnalitica(
            id=3, codigo="DELIBERACAO_PLENARIO", nome="Plenário", ordem_logica=3
        ),
        FaseAnalitica(
            id=4, codigo="TRAMITE_ENTRE_CASAS", nome="Handoff", ordem_logica=4
        ),
        FaseAnalitica(id=5, codigo="ETAPA_EXECUTIVO", nome="Executivo", ordem_logica=5),
        FaseAnalitica(id=6, codigo="ENCERRADA", nome="Encerrada", ordem_logica=6),
    ]


@pytest.fixture
def mock_repos(mock_fases):
    periodo_repo = MagicMock()
    evento_repo = MagicMock()
    fase_repo = MagicMock()
    proposicao_repo = MagicMock()

    fase_repo.buscar_todas.return_value = mock_fases

    return {
        "periodo_repo": periodo_repo,
        "evento_repo": evento_repo,
        "fase_repo": fase_repo,
        "proposicao_repo": proposicao_repo,
    }


@pytest.fixture
def service(mock_repos):
    return ReconstruirPeriodosService(
        periodo_repo=mock_repos["periodo_repo"],
        evento_repo=mock_repos["evento_repo"],
        fase_repo=mock_repos["fase_repo"],
        proposicao_repo=mock_repos["proposicao_repo"],
    )


def test_reconstruir_sem_eventos(service, mock_repos):
    # Arrange
    prop = Proposicao(
        id="PL-100",
        tipo="PL",
        numero="100",
        ano=2026,
        status="Sancionada",
        data_apresentacao="2026-01-01",
    )
    mock_repos["proposicao_repo"].buscar_por_id.return_value = prop
    mock_repos["evento_repo"].buscar_por_proposicao.return_value = []

    # Act
    periodos = service.reconstruir_para_proposicao("PL-100")

    # Assert
    assert len(periodos) == 1
    p = periodos[0]
    assert p.fase_analitica_id == 6  # ENCERRADA
    assert p.data_inicio == date(2026, 1, 1)
    assert p.data_fim is None
    assert p.eh_fase_atual is True
    assert p.recorrencia_numero == 1

    # Verify Proposicao was updated and saved
    mock_repos["proposicao_repo"].salvar.assert_called_once()
    saved_prop = mock_repos["proposicao_repo"].salvar.call_args[0][0]
    assert saved_prop.status == "Sancionada"
    assert saved_prop.data_encerramento == "2026-01-01"


def test_reconstruir_com_eventos_simples(service, mock_repos):
    # Arrange
    prop = Proposicao(
        id="PL-200",
        tipo="PL",
        numero="200",
        ano=2026,
        status="Em Tramitação",
        data_apresentacao="2026-01-01",
    )
    mock_repos["proposicao_repo"].buscar_por_id.return_value = prop

    eventos = [
        EventoTramitacao(
            proposicao_id="PL-200",
            data_evento="2026-01-01",
            sequencia=1,
            descricao_original="Apresentação",
            tipo_evento="APRESENTACAO",
            fase_analitica_id=1,
        ),
        EventoTramitacao(
            proposicao_id="PL-200",
            data_evento="2026-01-05",
            sequencia=1,
            descricao_original="Despacho às comissões",
            tipo_evento="RECEBIMENTO_ORGAO",
            fase_analitica_id=2,
        ),
        EventoTramitacao(
            proposicao_id="PL-200",
            data_evento="2026-01-10",
            sequencia=1,
            descricao_original="Discussão na CCJ",
            tipo_evento="VOTACAO_COMISSAO",
            fase_analitica_id=2,
            sigla_orgao="CCJ",
        ),
    ]
    mock_repos["evento_repo"].buscar_por_proposicao.return_value = eventos

    # Act
    periodos = service.reconstruir_para_proposicao("PL-200")

    # Assert
    assert len(periodos) == 2

    # Period 1: PROTOCOLO_INICIAL
    p1 = periodos[0]
    assert p1.fase_analitica_id == 1
    assert p1.data_inicio == date(2026, 1, 1)
    assert p1.data_fim == date(2026, 1, 5)
    assert p1.duracao_dias == 4
    assert p1.eh_fase_atual is False
    assert p1.recorrencia_numero == 1

    # Period 2: ANALISE_COMISSOES (contains two events)
    p2 = periodos[1]
    assert p2.fase_analitica_id == 2
    assert p2.data_inicio == date(2026, 1, 5)
    assert p2.data_fim is None
    assert p2.eh_fase_atual is True
    assert p2.recorrencia_numero == 1
    assert p2.subtipo_fase == "ccj"

    # Verify Proposicao update
    mock_repos["proposicao_repo"].salvar.assert_called_once()
    saved_prop = mock_repos["proposicao_repo"].salvar.call_args[0][0]
    assert saved_prop.status == "Em Tramitação"
    assert saved_prop.data_encerramento is None


def test_reconstruir_com_travamento(service, mock_repos):
    # Arrange
    prop = Proposicao(
        id="PL-300",
        tipo="PL",
        numero="300",
        ano=2026,
        status="Em Tramitação",
        data_apresentacao="2026-01-01",
    )
    mock_repos["proposicao_repo"].buscar_por_id.return_value = prop

    # Create a period with a duration > 30 days by making the last event over 30 days old
    data_inicio_str = (date.today() - timedelta(days=40)).isoformat()

    eventos = [
        EventoTramitacao(
            proposicao_id="PL-300",
            data_evento=data_inicio_str,
            sequencia=1,
            descricao_original="Prazo suspenso",
            tipo_evento="RECEBIMENTO_ORGAO",
            fase_analitica_id=2,
        )
    ]
    mock_repos["evento_repo"].buscar_por_proposicao.return_value = eventos

    # Act
    periodos = service.reconstruir_para_proposicao("PL-300")

    # Assert
    assert len(periodos) == 1
    p = periodos[0]
    assert p.motivo_travamento == "sobrestado"
