from unittest.mock import Mock

import pytest

from application.services.dashboard_service import DashboardService
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.fase_analitica import FaseAnalitica
from domain.entities.proposicao import Proposicao
from domain.entities.tipo_evento import TipoEvento


@pytest.fixture
def mock_repo():
    return Mock()


@pytest.fixture
def mock_evento_repo():
    repo = Mock()
    repo.buscar_por_multiplas_proposicoes.return_value = {}
    repo.contar_por_tipo.return_value = {}
    return repo


@pytest.fixture
def mock_dashboard_repo():
    return Mock()


def test_obter_metricas_vazio(mock_repo, mock_evento_repo, mock_dashboard_repo):
    mock_dashboard_repo.obter_metricas_gerais.return_value = {
        "totalProposicoes": 0,
        "totalAprovadas": 0,
        "totalEmTramitacao": 0,
        "proposicoesComAtraso": 0,
        "tempoMedioTramitacao": 0,
        "comissaoMaiorTempo": "N/A",
        "comissaoMaiorTempoMedia": 0,
    }
    service = DashboardService(
        mock_repo, mock_evento_repo, dashboard_repo=mock_dashboard_repo
    )

    metricas = service.obter_metricas()

    assert metricas["totalProposicoes"] == 0
    assert metricas["tempoMedioTramitacao"] == 0
    assert metricas["comissaoMaiorTempo"] == "N/A"
    mock_dashboard_repo.obter_metricas_gerais.assert_called_once()


def test_obter_metricas_com_dados(mock_repo, mock_evento_repo, mock_dashboard_repo):
    mock_dashboard_repo.obter_metricas_gerais.return_value = {
        "totalProposicoes": 2,
        "totalAprovadas": 1,
        "totalEmTramitacao": 1,
        "proposicoesComAtraso": 1,
        "tempoMedioTramitacao": 150,
        "comissaoMaiorTempo": "CFT",
        "comissaoMaiorTempoMedia": 200,
    }
    service = DashboardService(
        mock_repo, mock_evento_repo, dashboard_repo=mock_dashboard_repo
    )

    metricas = service.obter_metricas()

    assert metricas["totalProposicoes"] == 2
    assert metricas["totalAprovadas"] == 1
    assert metricas["totalEmTramitacao"] == 1
    assert metricas["proposicoesComAtraso"] == 1
    assert metricas["tempoMedioTramitacao"] == 150
    assert metricas["comissaoMaiorTempo"] == "CFT"
    assert metricas["comissaoMaiorTempoMedia"] == 200
    mock_dashboard_repo.obter_metricas_gerais.assert_called_once()


def test_obter_dados_tipo(mock_repo, mock_evento_repo, mock_dashboard_repo):
    mock_dashboard_repo.obter_dados_tipo.return_value = [
        {"tipo": "PL", "quantidade": 2, "tempoMedio": 150},
        {"tipo": "PEC", "quantidade": 1, "tempoMedio": 300},
    ]
    service = DashboardService(
        mock_repo, mock_evento_repo, dashboard_repo=mock_dashboard_repo
    )

    dados = service.obter_dados_tipo()

    # PL deve vir primeiro (quantidade 2)
    assert dados[0]["tipo"] == "PL"
    assert dados[0]["quantidade"] == 2
    assert dados[0]["tempoMedio"] == 150

    assert dados[1]["tipo"] == "PEC"
    assert dados[1]["quantidade"] == 1
    assert dados[1]["tempoMedio"] == 300
    mock_dashboard_repo.obter_dados_tipo.assert_called_once()


def test_obter_gargalos(mock_repo, mock_evento_repo, mock_dashboard_repo):
    mock_dashboard_repo.obter_gargalos.return_value = [
        {"orgao": "CCJ", "taxaAtraso": 100, "tempoMedioMeses": 10.0},
        {"orgao": "CFT", "taxaAtraso": 0, "tempoMedioMeses": 2.0},
    ]
    service = DashboardService(
        mock_repo, mock_evento_repo, dashboard_repo=mock_dashboard_repo
    )

    gargalos = service.obter_gargalos()

    assert gargalos[0]["orgao"] == "CCJ"
    assert gargalos[0]["taxaAtraso"] == 100
    assert gargalos[0]["tempoMedioMeses"] == 10.0  # 300 / 30

    assert gargalos[1]["orgao"] == "CFT"
    assert gargalos[1]["taxaAtraso"] == 0
    assert gargalos[1]["tempoMedioMeses"] == 2.0  # 60 / 30
    mock_dashboard_repo.obter_gargalos.assert_called_once()


def test_obter_dados_comissao(mock_repo, mock_evento_repo, mock_dashboard_repo):
    mock_dashboard_repo.obter_dados_comissao.return_value = [
        {"comissao": "Desconhecido", "quantidade": 1, "tempoMedio": 200},
        {"comissao": "CCJ", "quantidade": 1, "tempoMedio": 100},
    ]
    service = DashboardService(
        mock_repo, mock_evento_repo, dashboard_repo=mock_dashboard_repo
    )

    dados = service.obter_dados_comissao()

    assert len(dados) == 2
    # Ordenado por tempoMedio desc: Desconhecido (200) vem antes de CCJ (100)
    assert dados[0]["comissao"] == "Desconhecido"
    assert dados[1]["comissao"] == "CCJ"
    mock_dashboard_repo.obter_dados_comissao.assert_called_once()


def test_obter_dados_status_vazio(mock_repo, mock_evento_repo, mock_dashboard_repo):
    mock_dashboard_repo.obter_dados_status.return_value = []
    service = DashboardService(
        mock_repo, mock_evento_repo, dashboard_repo=mock_dashboard_repo
    )
    assert service.obter_dados_status() == []
    mock_dashboard_repo.obter_dados_status.assert_called_once()


def test_obter_dados_status_com_dados(mock_repo, mock_evento_repo, mock_dashboard_repo):
    mock_dashboard_repo.obter_dados_status.return_value = [
        {"status": "Aprovada/Sancionada", "quantidade": 2, "percentual": 67},
        {"status": "Em tramitação", "quantidade": 1, "percentual": 33},
    ]
    service = DashboardService(
        mock_repo, mock_evento_repo, dashboard_repo=mock_dashboard_repo
    )

    dados = service.obter_dados_status()

    assert len(dados) == 2
    # Aprovada: 2/3 = 67%
    aprovada = next(d for d in dados if d["status"] == "Aprovada/Sancionada")
    assert aprovada["quantidade"] == 2
    assert aprovada["percentual"] == 67
    mock_dashboard_repo.obter_dados_status.assert_called_once()


def test_obter_comparacao_temas(mock_repo, mock_evento_repo, mock_dashboard_repo):
    mock_dashboard_repo.obter_proposicoes_para_temas.return_value = [
        {
            "tags": ["Educação"],
            "tempo_total_dias": 100,
            "status_agrupado": "Aprovada/Sancionada",
        },
        {
            "tags": ["Educação", "Saúde"],
            "tempo_total_dias": 200,
            "status_agrupado": "Em tramitação",
        },
        {
            "tags": ["Saúde"],
            "tempo_total_dias": 700,
            "status_agrupado": "Rejeitada/Arquivada",
        },
    ]
    service = DashboardService(
        mock_repo, mock_evento_repo, dashboard_repo=mock_dashboard_repo
    )

    temas = service.obter_comparacao_temas()

    # Educação: 2 proposições, tempo médio (100+200)/2 = 150, aprovadas 1/2 = 50%
    educacao = next(t for t in temas if t["tema"] == "Educação")
    assert educacao["tempoMedioDias"] == 150
    assert educacao["taxaAprovacao"] == 50
    assert educacao["velocidade"] == "rapido"

    # Saúde: 2 proposições, tempo médio (200+700)/2 = 450, aprovadas 0/2 = 0%
    saude = next(t for t in temas if t["tema"] == "Saúde")
    assert saude["tempoMedioDias"] == 450
    assert saude["taxaAprovacao"] == 0
    assert saude["velocidade"] == "medio"

    mock_dashboard_repo.obter_proposicoes_para_temas.assert_called_once()


# --- Testes de obter_tempo_por_fase ---


def _fase(id_: int, codigo: str, nome: str, ordem: int) -> FaseAnalitica:
    f = FaseAnalitica(codigo=codigo, nome=nome, ordem_logica=ordem)
    f.id = id_
    return f


def _prop(id_: str) -> Proposicao:
    return Proposicao(
        id=id_,
        tipo="PL",
        numero="1",
        ano=2024,
        status="Em tramitação",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        orgao_atual="CCJ",
        tempo_total_dias=100,
    )


def _evento(prop_id: str, seq: int, data: str, fase_id: int) -> EventoTramitacao:
    return EventoTramitacao(
        proposicao_id=prop_id,
        sequencia=seq,
        data_evento=data,
        tipo_evento=TipoEvento.DESPACHO.value,
        descricao_original="",
        fase_analitica_id=fase_id,
    )


def test_obter_tempo_por_fase_sem_fase_repo(mock_repo, mock_evento_repo):
    """Sem fase_repo injetado, retorna lista vazia sem erros."""
    service = DashboardService(mock_repo, mock_evento_repo)
    assert service.obter_tempo_por_fase() == []


def test_obter_tempo_por_fase_sem_proposicoes(mock_repo, mock_evento_repo):
    """Sem proposições, retorna lista vazia."""
    fase_repo = Mock()
    fase_repo.buscar_todas.return_value = [
        _fase(1, "PROTOCOLO_INICIAL", "Protocolo inicial", 1)
    ]
    mock_repo.filtrar.return_value = []
    service = DashboardService(mock_repo, mock_evento_repo, fase_repo)
    assert service.obter_tempo_por_fase() == []


def test_obter_tempo_por_fase_eventos_sem_fase(mock_repo, mock_evento_repo):
    """Eventos com fase_analitica_id=None são ignorados; retorna lista vazia."""
    fase_repo = Mock()
    fase_repo.buscar_todas.return_value = [
        _fase(1, "PROTOCOLO_INICIAL", "Protocolo inicial", 1)
    ]
    prop = _prop("1")
    mock_repo.filtrar.return_value = [prop]
    evento_sem_fase = EventoTramitacao(
        proposicao_id="1",
        sequencia=1,
        data_evento="2024-01-01",
        tipo_evento=TipoEvento.DESPACHO.value,
        descricao_original="",
        fase_analitica_id=None,
    )
    mock_evento_repo.buscar_por_multiplas_proposicoes.return_value = {
        "1": [evento_sem_fase]
    }
    service = DashboardService(mock_repo, mock_evento_repo, fase_repo)
    assert service.obter_tempo_por_fase() == []


def test_obter_tempo_por_fase_uma_proposicao_duas_fases(mock_repo, mock_evento_repo):
    """
    Proposição com 2 fases: 30 dias na fase 1, depois entra na fase 2.
    A última fase conta até hoje — não verificamos o valor exato, só que está presente.
    """
    fase_repo = Mock()
    fase_repo.buscar_todas.return_value = [
        _fase(1, "PROTOCOLO_INICIAL", "Protocolo inicial", 1),
        _fase(2, "ANALISE_COMISSOES", "Análise em comissões", 2),
    ]
    prop = _prop("1")
    mock_repo.filtrar.return_value = [prop]
    mock_evento_repo.buscar_por_multiplas_proposicoes.return_value = {
        "1": [
            _evento("1", 1, "2024-01-01", 1),
            _evento("1", 2, "2024-01-10", 1),
            _evento("1", 3, "2024-01-31", 2),  # transição: 30 dias na fase 1
            _evento("1", 4, "2024-02-15", 2),
        ]
    }
    service = DashboardService(mock_repo, mock_evento_repo, fase_repo)
    resultado = service.obter_tempo_por_fase()

    assert len(resultado) == 2
    # ordenado por ordemLogica
    assert resultado[0]["codigoFase"] == "PROTOCOLO_INICIAL"
    assert resultado[0]["ordemLogica"] == 1
    assert resultado[0]["tempoMedioDias"] == 30  # 2024-01-31 - 2024-01-01
    assert resultado[0]["quantidadeProposicoes"] == 1

    assert resultado[1]["codigoFase"] == "ANALISE_COMISSOES"
    assert resultado[1]["ordemLogica"] == 2
    assert resultado[1]["quantidadeProposicoes"] == 1


def test_obter_tempo_por_fase_agrega_multiplas_proposicoes(mock_repo, mock_evento_repo):
    """Duas proposições na mesma fase: tempo médio é calculado corretamente."""
    fase_repo = Mock()
    fase_repo.buscar_todas.return_value = [
        _fase(1, "PROTOCOLO_INICIAL", "Protocolo inicial", 1),
    ]
    p1 = _prop("1")
    p2 = _prop("2")
    mock_repo.filtrar.return_value = [p1, p2]
    mock_evento_repo.buscar_por_multiplas_proposicoes.return_value = {
        # p1: 10 dias na fase 1, depois transição (sem fase 2)
        "1": [
            _evento("1", 1, "2024-01-01", 1),
            _evento("1", 2, "2024-01-11", 1),  # saída registrada ao fim
        ],
        # p2: 20 dias na fase 1
        "2": [
            _evento("2", 1, "2024-02-01", 1),
            _evento("2", 2, "2024-02-21", 1),
        ],
    }
    service = DashboardService(mock_repo, mock_evento_repo, fase_repo)
    resultado = service.obter_tempo_por_fase()

    # Ambas ficaram na fase 1; a última fase usa date.today() como saída.
    # Não testamos o valor exato (depende de date.today()), mas verificamos estrutura.
    assert len(resultado) == 1
    assert resultado[0]["codigoFase"] == "PROTOCOLO_INICIAL"
    assert resultado[0]["quantidadeProposicoes"] == 2


def test_obter_tempo_por_fase_ordena_por_ordem_logica(mock_repo, mock_evento_repo):
    """Resultado deve estar ordenado por ordemLogica crescente."""
    fase_repo = Mock()
    # seed retornado fora de ordem intencional
    fase_repo.buscar_todas.return_value = [
        _fase(3, "DELIBERACAO_PLENARIO", "Deliberação em plenário", 4),
        _fase(1, "PROTOCOLO_INICIAL", "Protocolo inicial", 1),
        _fase(2, "ANALISE_COMISSOES", "Análise em comissões", 2),
    ]
    prop = _prop("1")
    mock_repo.filtrar.return_value = [prop]
    mock_evento_repo.buscar_por_multiplas_proposicoes.return_value = {
        "1": [
            _evento("1", 1, "2024-01-01", 1),
            _evento("1", 2, "2024-02-01", 2),
            _evento("1", 3, "2024-03-01", 3),
        ]
    }
    service = DashboardService(mock_repo, mock_evento_repo, fase_repo)
    resultado = service.obter_tempo_por_fase()

    ordens = [r["ordemLogica"] for r in resultado]
    assert ordens == sorted(ordens)
