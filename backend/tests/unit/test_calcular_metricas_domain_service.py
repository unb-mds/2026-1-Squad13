from datetime import date, timedelta

from domain.entities.evento_tramitacao import EventoTramitacao
from domain.services.calcular_metricas_service import CalcularMetricasService


def test_obter_decorrido_e_encerramento_ativa():
    # Arrange
    apresentacao = (date.today() - timedelta(days=10)).isoformat()
    eventos = [
        EventoTramitacao(
            proposicao_id="123",
            data_evento=apresentacao,
            sequencia=1,
            tipo_evento="APRESENTACAO",
            descricao_original="Apresentação",
        )
    ]

    # Act
    decorrido, encerramento = CalcularMetricasService.obter_decorrido_e_encerramento(
        apresentacao, eventos
    )

    # Assert
    assert decorrido == 10
    assert encerramento is None


def test_obter_decorrido_e_encerramento_concluida():
    # Arrange
    apresentacao = "2026-05-01"
    evento_fim_data = "2026-05-15"
    eventos = [
        EventoTramitacao(
            proposicao_id="123",
            data_evento=apresentacao,
            sequencia=1,
            tipo_evento="APRESENTACAO",
            descricao_original="Apresentação",
        ),
        EventoTramitacao(
            proposicao_id="123",
            data_evento=evento_fim_data,
            sequencia=2,
            tipo_evento="PROMULGACAO",  # Evento terminal
            descricao_original="Promulgação",
        ),
    ]

    # Act
    decorrido, encerramento = CalcularMetricasService.obter_decorrido_e_encerramento(
        apresentacao, eventos
    )

    # Assert
    assert decorrido == 14  # 15 - 1
    assert encerramento == "2026-05-15"


def test_calcular_iar():
    assert CalcularMetricasService.calcular_iar(100, 50) == 2.0
    assert CalcularMetricasService.calcular_iar(100, 0) is None
    assert CalcularMetricasService.calcular_iar(10, 100) == 0.1


def test_classificar_status_atraso():
    assert (
        CalcularMetricasService.classificar_status_atraso(None)
        == "INSUFICIENTE_BASELINE"
    )
    assert CalcularMetricasService.classificar_status_atraso(0.9) == "NO_PRAZO"
    assert CalcularMetricasService.classificar_status_atraso(1.2) == "ATENCAO"
    assert CalcularMetricasService.classificar_status_atraso(1.8) == "ATRASADA"
    assert CalcularMetricasService.classificar_status_atraso(2.5) == "CRITICA"
    assert CalcularMetricasService.classificar_status_atraso(3.0) == "CRITICA"


def test_calcular_iei():
    # Arrange
    eventos = [
        # Evento improdutivo (deliberativo=False, mudou_fase=False, mudou_orgao=False)
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2026-05-01",
            sequencia=1,
            tipo_evento="DESPACHO",
            descricao_original="Despacho ordinário",
            dias_na_etapa=10,
            deliberativo=False,
            mudou_fase=False,
            mudou_orgao=False,
        ),
        # Evento produtivo (deliberativo=True)
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2026-05-11",
            sequencia=2,
            tipo_evento="VOTACAO_COMISSAO",
            descricao_original="Votação em comissão",
            dias_na_etapa=5,
            deliberativo=True,
            mudou_fase=False,
            mudou_orgao=False,
        ),
        # Evento produtivo (mudou_fase=True)
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2026-05-16",
            sequencia=3,
            tipo_evento="INCLUSAO_PAUTA",
            descricao_original="Inclusão em pauta",
            dias_na_etapa=8,
            deliberativo=False,
            mudou_fase=True,
            mudou_orgao=False,
        ),
    ]

    # Act & Assert
    assert CalcularMetricasService.calcular_iei(eventos, 23) == round(10 / 23, 4)
    assert CalcularMetricasService.calcular_iei(eventos, 0) == 0.0


def test_obter_data_entrada_fase_atual():
    # Arrange
    apresentacao = "2026-05-01"
    eventos = [
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2026-05-01",
            sequencia=1,
            tipo_evento="APRESENTACAO",
            descricao_original="Apresentação",
            fase_analitica_id=1,
        ),
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2026-05-05",
            sequencia=2,
            tipo_evento="RECEBIMENTO_ORGAO",
            descricao_original="Recebimento no órgão",
            fase_analitica_id=2,  # Entrou na fase 2
        ),
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2026-05-10",
            sequencia=3,
            tipo_evento="DESIGNACAO_RELATOR",
            descricao_original="Designação de relator",
            fase_analitica_id=2,  # Permaneceu na fase 2
        ),
    ]

    # Act
    fase_id, data_entrada = CalcularMetricasService.obter_data_entrada_fase_atual(
        apresentacao, eventos
    )

    # Assert
    assert fase_id == 2
    assert data_entrada == "2026-05-05"


def test_calcular_iaf():
    # Arrange
    data_entrada = (date.today() - timedelta(days=20)).isoformat()

    # Act & Assert
    assert CalcularMetricasService.calcular_iaf(data_entrada, 10, None) == 2.0
    assert (
        CalcularMetricasService.calcular_iaf(data_entrada, 10, "2026-05-20") is None
    )  # Encerrada
    assert CalcularMetricasService.calcular_iaf(data_entrada, 0, None) is None
