from domain.entities.evento_tramitacao import EventoTramitacao, calcular_tempo_por_fase


def test_calcular_tempo_por_fase_sem_dados_suficientes():
    eventos = [
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2023-01-01",
            sequencia=1,
            descricao_original="",
            tipo_evento="APRESENTACAO",
        )
    ]
    assert calcular_tempo_por_fase(eventos) == []
    assert calcular_tempo_por_fase([]) == []


def test_calcular_tempo_por_fase_com_dados():
    eventos = [
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2023-01-01",
            sequencia=1,
            descricao_original="",
            tipo_evento="APRESENTACAO",
            sigla_orgao="PLEN",
        ),
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2023-01-10",
            sequencia=2,
            descricao_original="",
            tipo_evento="RECEBIMENTO_ORGAO",
            sigla_orgao="CCJC",
        ),
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2023-01-15",
            sequencia=3,
            descricao_original="",
            tipo_evento="RECEBIMENTO_ORGAO",
            sigla_orgao="CIND",
        ),
    ]

    resultado = calcular_tempo_por_fase(eventos)

    assert len(resultado) == 2
    assert resultado[0] == {"fase": "PLEN", "dias": 9}
    assert resultado[1] == {"fase": "CCJC", "dias": 5}


def test_calcular_tempo_por_fase_mesma_fase_acumula():
    eventos = [
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2023-01-01",
            sequencia=1,
            descricao_original="",
            tipo_evento="APRESENTACAO",
            sigla_orgao="PLEN",
        ),
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2023-01-10",
            sequencia=2,
            descricao_original="",
            tipo_evento="RECEBIMENTO_ORGAO",
            sigla_orgao="CCJC",
        ),
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2023-01-15",
            sequencia=3,
            descricao_original="",
            tipo_evento="RECEBIMENTO_ORGAO",
            sigla_orgao="PLEN",
        ),
        EventoTramitacao(
            proposicao_id="1",
            data_evento="2023-01-20",
            sequencia=4,
            descricao_original="",
            tipo_evento="RECEBIMENTO_ORGAO",
            sigla_orgao="MESA",
        ),
    ]

    resultado = calcular_tempo_por_fase(eventos)

    assert len(resultado) == 2
    assert resultado[0] == {"fase": "PLEN", "dias": 14}
    assert resultado[1] == {"fase": "CCJC", "dias": 5}
