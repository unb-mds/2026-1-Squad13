from datetime import datetime

from .types import FSMState, House, InputType, StepRole


def transition(
    state: FSMState, input_type: InputType, event_timestamp: datetime
) -> FSMState:
    proxima_casa = state.casa_ativa
    gatilho_foi_implicito = False

    # Regras de Transição da Máquina de Estados
    if state.casa_ativa == House.CAMARA:
        if input_type == InputType.GATILHO_REMESSA:
            proxima_casa = House.SENADO
            gatilho_foi_implicito = False
        elif input_type == InputType.EXCLUSIVO_SENADO:
            # Invariante 5: Auto-correção implícita única por fronteira temporal
            if not state.ultimo_gatilho_foi_implicito:
                proxima_casa = House.SENADO
                gatilho_foi_implicito = True
    else:  # House.SENADO
        if (
            input_type == InputType.GATILHO_RETORNO
            or input_type == InputType.GATILHO_REMESSA
        ):
            proxima_casa = House.CAMARA
            gatilho_foi_implicito = False
        elif input_type == InputType.EXCLUSIVO_CAMARA:
            # Invariante 5: Auto-correção implícita anti-ping-pong
            if not state.ultimo_gatilho_foi_implicito:
                proxima_casa = House.CAMARA
                gatilho_foi_implicito = True

    # Atualização da última Casa com certeza absoluta (Invariante 4)
    nova_certeza = (
        proxima_casa
        if input_type in (InputType.EXCLUSIVO_CAMARA, InputType.EXCLUSIVO_SENADO)
        else state.ultima_casa_nao_ambigua
    )

    # Estado de controle para classificar papel sem dependência de tempo
    proximo_ja_passou_revisora = state.ja_passou_pela_revisora or (
        proxima_casa != state.casa_origem
    )

    # Invariante 8: Determinação de papel por percurso semântico puro (sem dependência de timestamp)
    novo_tipo = StepRole.ORIGEM
    if proxima_casa != state.casa_origem:
        novo_tipo = StepRole.REVISORA
    elif proximo_ja_passou_revisora:
        novo_tipo = StepRole.RETORNO

    mudou_de_casa = proxima_casa != state.casa_ativa

    return FSMState(
        casa_ativa=proxima_casa,
        tipo_passo=novo_tipo,
        timestamp_entrada=event_timestamp if mudou_de_casa else state.timestamp_entrada,
        casa_origem=state.casa_origem,
        ultima_casa_nao_ambigua=nova_certeza,
        ja_passou_pela_revisora=proximo_ja_passou_revisora,
        ultimo_gatilho_foi_implicito=gatilho_foi_implicito
        if mudou_de_casa
        else state.ultimo_gatilho_foi_implicito,
    )
