from unittest.mock import Mock
from domain.entities.proposicao import Proposicao
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.tipo_evento import TipoEvento
from application.services.dashboard_service import DashboardService


def _mock_proposicao(id_str, status, tempo=None):
    return Proposicao(
        id=id_str,
        tipo="PL",
        numero="123",
        ano=2024,
        autor="Autor",
        orgao_origem="Câmara",
        status=status,
        ementa="Ementa",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        orgao_atual="CCJ",
        tags=[],
        tempo_total_dias=tempo,
    )


def test_dashboard_service_analitico_calculo_tempo(monkeypatch):
    prop_repo = Mock()
    evento_repo = Mock()

    # Proposição baseada em eventos (60 dias de tramitação até arquivamento)
    prop1 = _mock_proposicao("1", "Em Tramitação", 0)
    eventos_prop1 = [
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2024-01-01T10:00:00",
            sequencia=1,
            tipo_evento=TipoEvento.APRESENTACAO.value,
            descricao_original="",
        ),
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2024-03-01T10:00:00",  # 60 dias depois
            sequencia=2,
            tipo_evento=TipoEvento.ARQUIVAMENTO.value,
            descricao_original="",
        ),
    ]

    # Proposição sem eventos (deve usar fallback)
    prop2 = _mock_proposicao("2", "Aprovada", 100)
    eventos_prop2 = []

    prop_repo.filtrar.return_value = [prop1, prop2]

    evento_repo.buscar_por_multiplas_proposicoes.return_value = {
        "1": eventos_prop1,
        "2": eventos_prop2,
    }

    service = DashboardService(prop_repo, evento_repo)
    metricas = service.obter_metricas()

    assert metricas["totalProposicoes"] == 2
    # tempo_total_dias médio: (60 + 100) / 2 = 80
    assert metricas["tempoMedioTramitacao"] == 80

    # Status atual de prop1 passa a ser Arquivada por conta dos eventos
    assert (
        metricas["totalRejeitadas"] == 1
    )  # prop1 (arquivamento -> rejeitada/arquivada)
    assert metricas["totalAprovadas"] == 1  # prop2 (fallback "Aprovada")


def test_dashboard_service_status_atual():
    prop_repo = Mock()
    evento_repo = Mock()
    service = DashboardService(prop_repo, evento_repo)

    eventos = [
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2024-01-01T10:00:00",
            sequencia=1,
            tipo_evento=TipoEvento.APRESENTACAO.value,
            descricao_original="",
        ),
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2024-02-01T10:00:00",
            sequencia=2,
            tipo_evento=TipoEvento.APROVACAO.value,
            descricao_original="",
        ),
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2024-02-05T10:00:00",
            sequencia=3,
            tipo_evento=TipoEvento.NAO_CLASSIFICADO.value,  # NAO_CLASSIFICADO deve ser ignorado para status atual
            descricao_original="",
        ),
    ]

    status = service._extrair_status_atual(eventos, "Fallback")
    assert status == "Aprovada"


def test_dashboard_service_atraso_critico():
    prop_repo = Mock()
    evento_repo = Mock()
    service = DashboardService(prop_repo, evento_repo)

    # 190 dias (atraso crítico)
    eventos_atraso = [
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2024-01-01T10:00:00",
            sequencia=1,
            tipo_evento=TipoEvento.APRESENTACAO.value,
            descricao_original="",
        ),
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2024-07-09T10:00:00",  # 190 dias
            sequencia=2,
            tipo_evento=TipoEvento.APROVACAO.value,
            descricao_original="",
        ),
    ]

    tempo = service._calcular_tempo_total(eventos_atraso, 0)
    assert tempo == 190
