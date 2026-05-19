from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.tipo_evento import TipoEvento


def test_eh_relevante_tipo_sempre_relevante():
    evento = EventoTramitacao(
        proposicao_id="1",
        data_evento="2024-05-14T10:00:00",
        sequencia=1,
        tipo_evento=TipoEvento.APROVACAO.value,
        descricao_original="Teste",
        mudou_fase=False,
        deliberativo=False,
        dias_na_etapa=0,
    )
    assert evento.eh_relevante is True


def test_eh_relevante_mudou_fase():
    evento = EventoTramitacao(
        proposicao_id="1",
        data_evento="2024-05-14T10:00:00",
        sequencia=1,
        tipo_evento=TipoEvento.NAO_CLASSIFICADO.value,
        descricao_original="Teste",
        mudou_fase=True,
        deliberativo=False,
        dias_na_etapa=0,
    )
    assert evento.eh_relevante is True


def test_eh_relevante_deliberativo():
    evento = EventoTramitacao(
        proposicao_id="1",
        data_evento="2024-05-14T10:00:00",
        sequencia=1,
        tipo_evento=TipoEvento.NAO_CLASSIFICADO.value,
        descricao_original="Teste",
        mudou_fase=False,
        deliberativo=True,
        dias_na_etapa=0,
    )
    assert evento.eh_relevante is True


def test_eh_relevante_tempo_longo():
    evento = EventoTramitacao(
        proposicao_id="1",
        data_evento="2024-05-14T10:00:00",
        sequencia=1,
        tipo_evento=TipoEvento.NAO_CLASSIFICADO.value,
        descricao_original="Teste",
        mudou_fase=False,
        deliberativo=False,
        dias_na_etapa=31,
    )
    assert evento.eh_relevante is True


def test_eh_relevante_marca_apensacao():
    evento = EventoTramitacao(
        proposicao_id="1",
        data_evento="2024-05-14T10:00:00",
        sequencia=1,
        tipo_evento=TipoEvento.APENSAMENTO.value,
        descricao_original="Teste",
        mudou_fase=False,
        deliberativo=False,
        dias_na_etapa=0,
        marca_apensacao=True,
    )
    assert evento.eh_relevante is True


def test_eh_relevante_ruido_puro():
    evento = EventoTramitacao(
        proposicao_id="1",
        data_evento="2024-05-14T10:00:00",
        sequencia=1,
        tipo_evento=TipoEvento.NAO_CLASSIFICADO.value,
        descricao_original="Teste",
        mudou_fase=False,
        deliberativo=False,
        dias_na_etapa=0,
        marca_apensacao=False,
    )
    assert evento.eh_relevante is False
