import random
from datetime import UTC, datetime, timedelta

from domain.fsm import (
    EventData,
    FSMState,
    House,
    InputType,
    StepRole,
    build_transit_steps,
)
from domain.fsm.classify import classify_event
from domain.fsm.transition import transition


# ----------------------------------------------------
# CAMADA 1: Testes do Classificador (classify_event)
# ----------------------------------------------------
def test_classifica_gatilhos_explicitos():
    e_remessa = EventData(
        timestamp=datetime.utcnow(),
        sigla_orgao="",
        orgao_nome="",
        descricao="",
        remessa_ou_retorno="REMESSA",
    )
    e_retorno = EventData(
        timestamp=datetime.utcnow(),
        sigla_orgao="",
        orgao_nome="",
        descricao="",
        remessa_ou_retorno="RETORNO",
    )
    assert classify_event(e_remessa) == InputType.GATILHO_REMESSA
    assert classify_event(e_retorno) == InputType.GATILHO_RETORNO


def test_classifica_remessa_por_regex_textual():
    e = EventData(
        timestamp=datetime.utcnow(),
        sigla_orgao="MESA",
        orgao_nome="",
        descricao="Remessa ao Senado Federal por meio do of. nº 288/2019/PS-GSE.",
        remessa_ou_retorno=None,
    )
    assert classify_event(e) == InputType.GATILHO_REMESSA


def test_classifica_retorno_por_regex_textual():
    # Do ponto de vista do Senado
    e_senado = EventData(
        timestamp=datetime.utcnow(),
        sigla_orgao="SEXPE",
        orgao_nome="",
        descricao="Remetida à Câmara dos Deputados comunicando aprovação.",
        remessa_ou_retorno=None,
    )
    assert classify_event(e_senado) == InputType.GATILHO_RETORNO

    # Do ponto de vista da Câmara
    e_camara = EventData(
        timestamp=datetime.utcnow(),
        sigla_orgao="MESA",
        orgao_nome="",
        descricao="Recebido o ofício nº 472/22 do senado federal com emendas.",
        remessa_ou_retorno=None,
    )
    assert classify_event(e_camara) == InputType.GATILHO_RETORNO


def test_classifica_siglas_exclusivas_senado():
    assert (
        classify_event(EventData(datetime.utcnow(), "SLSF", "", "", None))
        == InputType.EXCLUSIVO_SENADO
    )
    assert (
        classify_event(EventData(datetime.utcnow(), "SEADI", "", "", None))
        == InputType.EXCLUSIVO_SENADO
    )
    assert (
        classify_event(EventData(datetime.utcnow(), "CAE", "", "", None))
        == InputType.EXCLUSIVO_SENADO
    )
    assert (
        classify_event(EventData(datetime.utcnow(), "SACDH", "", "", None))
        == InputType.EXCLUSIVO_SENADO
    )


def test_classifica_siglas_exclusivas_camara():
    assert (
        classify_event(EventData(datetime.utcnow(), "CCJC", "", "", None))
        == InputType.EXCLUSIVO_CAMARA
    )
    assert (
        classify_event(EventData(datetime.utcnow(), "CFT", "", "", None))
        == InputType.EXCLUSIVO_CAMARA
    )
    assert (
        classify_event(EventData(datetime.utcnow(), "CCP", "", "", None))
        == InputType.EXCLUSIVO_CAMARA
    )

    # CPASF não deve colidir com a checagem frouxa de "sf" do Senado!
    assert (
        classify_event(EventData(datetime.utcnow(), "CPASF", "", "", None))
        == InputType.EXCLUSIVO_CAMARA
    )


def test_classifica_siglas_ambiguas_ou_neutras():
    assert (
        classify_event(EventData(datetime.utcnow(), "CE", "", "", None))
        == InputType.AMBIGUO_OU_NEUTRO
    )
    assert (
        classify_event(EventData(datetime.utcnow(), "MESA", "", "", None))
        == InputType.AMBIGUO_OU_NEUTRO
    )
    assert (
        classify_event(EventData(datetime.utcnow(), "PLEN", "", "", None))
        == InputType.AMBIGUO_OU_NEUTRO
    )


# ----------------------------------------------------
# CAMADA 2: Testes da Transição FSM (transition)
# ----------------------------------------------------
def test_transition_camara_para_senado():
    state = FSMState(
        casa_ativa=House.CAMARA,
        tipo_passo=StepRole.ORIGEM,
        timestamp_entrada=datetime(2026, 1, 1),
        casa_origem=House.CAMARA,
        ultima_casa_nao_ambigua=House.CAMARA,
        ja_passou_pela_revisora=False,
        ultimo_gatilho_foi_implicito=False,
    )
    next_state = transition(state, InputType.GATILHO_REMESSA, datetime(2026, 1, 2))
    assert next_state.casa_ativa == House.SENADO
    assert next_state.tipo_passo == StepRole.REVISORA
    assert next_state.ja_passou_pela_revisora is True
    assert next_state.ultimo_gatilho_foi_implicito is False


def test_transition_auto_correcao_unica_por_fronteira_temporal():
    # Primeira correção implícita
    state = FSMState(
        casa_ativa=House.CAMARA,
        tipo_passo=StepRole.ORIGEM,
        timestamp_entrada=datetime(2026, 1, 1),
        casa_origem=House.CAMARA,
        ultima_casa_nao_ambigua=House.CAMARA,
        ja_passou_pela_revisora=False,
        ultimo_gatilho_foi_implicito=False,
    )
    next_state = transition(state, InputType.EXCLUSIVO_SENADO, datetime(2026, 1, 2))
    assert next_state.casa_ativa == House.SENADO
    assert next_state.ultimo_gatilho_foi_implicito is True

    # Bloqueio de correção consecutiva consecutiva sem gatilho explícito
    blocked_state = transition(
        next_state, InputType.EXCLUSIVO_CAMARA, datetime(2026, 1, 3)
    )
    assert blocked_state.casa_ativa == House.SENADO  # Permanece no Senado


def test_transition_self_loops():
    state = FSMState(
        casa_ativa=House.SENADO,
        tipo_passo=StepRole.REVISORA,
        timestamp_entrada=datetime(2026, 1, 1),
        casa_origem=House.CAMARA,
        ultima_casa_nao_ambigua=House.SENADO,
        ja_passou_pela_revisora=True,
        ultimo_gatilho_foi_implicito=False,
    )
    next_state = transition(state, InputType.AMBIGUO_OU_NEUTRO, datetime(2026, 1, 2))
    assert next_state.casa_ativa == House.SENADO
    assert next_state.timestamp_entrada == datetime(
        2026, 1, 1
    )  # Preserva data de entrada


# ----------------------------------------------------
# CAMADA 3: Integração e Invariantes Formais
# ----------------------------------------------------
def _generate_random_sequence():
    inputs = [
        "GATILHO_REMESSA",
        "GATILHO_RETORNO",
        "EXCLUSIVO_CAMARA",
        "EXCLUSIVO_SENADO",
        "AMBIGUO_OU_NEUTRO",
    ]
    events = []
    base_time = datetime(2026, 1, 1)

    count = random.randint(10, 50)
    for _ in range(count):
        base_time += timedelta(days=random.randint(1, 5))
        input_type = random.choice(inputs)

        sigla = "CE"
        desc = "Evento neutro"
        remessa = None

        if input_type == "GATILHO_REMESSA":
            desc = "Remessa ao senado federal"
        elif input_type == "GATILHO_RETORNO":
            desc = "Recebido o ofício do senado federal"
        elif input_type == "EXCLUSIVO_SENADO":
            sigla = "SLSF"
        elif input_type == "EXCLUSIVO_CAMARA":
            sigla = "CCJC"

        events.append(
            EventData(
                timestamp=base_time,
                sigla_orgao=sigla,
                orgao_nome="",
                descricao=desc,
                remessa_ou_retorno=remessa,
            )
        )
    return events


def test_prova_invariantes_em_500_execucoes():
    for _ in range(500):
        casa_origem = random.choice([House.CAMARA, House.SENADO])
        events = _generate_random_sequence()

        steps = build_transit_steps(events, casa_origem)

        # Invariante 2: Inicialização
        assert steps[0].casa == casa_origem

        # Invariante 7: Correspondência biunívoca (Não pode ter consecutivos na mesma casa)
        for i in range(len(steps) - 1):
            assert steps[i].casa != steps[i + 1].casa

        # Invariante 8: Coerência de Papel por Percurso
        for idx, step in enumerate(steps):
            if step.casa != casa_origem:
                assert step.tipo_passo == StepRole.REVISORA
            elif idx == 0:
                assert step.tipo_passo == StepRole.ORIGEM
            else:
                assert step.tipo_passo == StepRole.RETORNO

        # Invariante 9: Continuidade Temporal (Sem Lacunas)
        for i in range(len(steps) - 1):
            assert steps[i].data_saida == steps[i + 1].data_entrada

        # Invariante 10: Conservação de Duração Total
        sorted_events = sorted(events, key=lambda x: x.timestamp)
        first_time = sorted_events[0].timestamp
        now = datetime.now(UTC) if first_time.tzinfo else datetime.now()
        expected_total_duration = int((now - first_time).total_seconds() / (24 * 3600))
        total_duration = sum(s.duracao_dias for s in steps)

        assert abs(total_duration - expected_total_duration) <= 1


# ----------------------------------------------------
# CAMADA 4: Casos de Regressão Real do Projeto
# ----------------------------------------------------
def test_regressao_pec_35_2011():
    eventos_pec = [
        EventData(datetime(2011, 5, 18), "SLSF", "", "Apresentação de PEC", None),
        EventData(datetime(2011, 6, 1), "CCJ", "", "Aprovação na comissão", None),
        EventData(
            datetime(2011, 8, 31),
            "SEXPE",
            "",
            "Remetida à Câmara dos Deputados",
            "REMESSA",
        ),
        EventData(
            datetime(2011, 9, 1),
            "CCJC",
            "",
            "Recebimento pela Câmara dos Deputados",
            None,
        ),
        EventData(
            datetime(2011, 12, 15), "PLEN", "", "Aprovação no Plenário da Câmara", None
        ),
    ]

    steps = build_transit_steps(eventos_pec, House.SENADO)

    # 2 passos: Senado (origem) -> Câmara (revisora)
    assert len(steps) == 2
    assert steps[0].casa == House.SENADO
    assert steps[0].tipo_passo == StepRole.ORIGEM
    assert steps[1].casa == House.CAMARA
    assert steps[1].tipo_passo == StepRole.REVISORA

    # Continuidade
    assert steps[0].data_saida == datetime(2011, 8, 31)
    assert steps[1].data_entrada == datetime(2011, 8, 31)


def test_regressao_pl_5026_2019():
    eventos_pl = [
        EventData(datetime(2017, 5, 24), "MESA", "", "Apresentação", None),
        EventData(datetime(2017, 6, 1), "CE", "", "Distribuição na Câmara", None),
        EventData(
            datetime(2019, 8, 28), "MESA", "", "Remessa ao senado federal", "REMESSA"
        ),
        EventData(
            datetime(2019, 9, 11),
            "SLSF",
            "",
            "Matéria lida em plenário do Senado",
            None,
        ),
        EventData(
            datetime(2020, 2, 18), "SACDH", "", "Aprovado parecer do senado", None
        ),
        EventData(
            datetime(2022, 5, 25), "SEADI", "", "Aprovada no Plenário do Senado", None
        ),
        EventData(
            datetime(2022, 6, 1),
            "SEXPE",
            "",
            "Remetida à Câmara dos Deputados",
            "RETORNO",
        ),
        EventData(
            datetime(2022, 6, 1),
            "MESA",
            "",
            "Recebido o ofício do senado federal",
            "RETORNO",
        ),
        EventData(datetime(2022, 6, 2), "CE", "", "Distribuição na Câmara", None),
        EventData(
            datetime(2025, 12, 3),
            "CPASF",
            "",
            "Aprovada na comissão de previdência",
            None,
        ),
    ]

    steps = build_transit_steps(eventos_pl, House.CAMARA)

    # 3 passos: Câmara (origem) -> Senado (revisora) -> Câmara (retorno)
    assert len(steps) == 3
    assert steps[0].casa == House.CAMARA
    assert steps[0].tipo_passo == StepRole.ORIGEM
    assert steps[1].casa == House.SENADO
    assert steps[1].tipo_passo == StepRole.REVISORA
    assert steps[2].casa == House.CAMARA
    assert steps[2].tipo_passo == StepRole.RETORNO

    # O evento de 02/06/2022 na "CE" da Câmara não deve causar oscilação
    assert steps[2].data_entrada == datetime(2022, 6, 1)
