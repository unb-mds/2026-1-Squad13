from datetime import UTC, datetime

from .classify import classify_event
from .transition import transition
from .types import EventData, FSMState, House, StepRole, TransitStep


def build_transit_steps(
    events: list[EventData], casa_origem: House
) -> list[TransitStep]:
    if not events:
        # Se não há eventos, retorna passo inicial simbólico
        return [
            TransitStep(
                casa=casa_origem,
                tipo_passo=StepRole.ORIGEM,
                data_entrada=datetime.now(UTC),
            )
        ]

    # Ordena cronologicamente por timestamp do evento
    sorted_events = sorted(events, key=lambda x: x.timestamp)

    first_event = sorted_events[0]
    first_event_time = first_event.timestamp

    # Inicializa o Estado (Invariante 2)
    state = FSMState(
        casa_ativa=casa_origem,
        tipo_passo=StepRole.ORIGEM,
        timestamp_entrada=first_event_time,
        casa_origem=casa_origem,
        ultima_casa_nao_ambigua=casa_origem,
        ja_passou_pela_revisora=False,
        ultimo_gatilho_foi_implicito=False,
    )

    steps: list[TransitStep] = []

    # Adiciona o passo inicial
    steps.append(
        TransitStep(
            casa=state.casa_ativa,
            tipo_passo=state.tipo_passo,
            data_entrada=state.timestamp_entrada,
        )
    )

    house_entry_time = first_event_time

    for i in range(1, len(sorted_events)):
        ev = sorted_events[i]
        ev_time = ev.timestamp
        input_type = classify_event(ev)

        next_state = transition(state, input_type, ev_time)

        # Invariante 7: Correspondência biunívoca (Novo TransitStep sse casa mudou)
        if next_state.casa_ativa != state.casa_ativa:
            # Fecha o passo anterior
            steps[-1].data_saida = ev_time
            steps[-1].duracao_dias = max(
                1, int((ev_time - house_entry_time).total_seconds() / (24 * 3600))
            )

            # Inicia novo passo
            steps.append(
                TransitStep(
                    casa=next_state.casa_ativa,
                    tipo_passo=next_state.tipo_passo,
                    data_entrada=ev_time,
                )
            )

            house_entry_time = ev_time

        state = next_state

    # Duração do último passo (até o momento atual)
    # Mantém timezone aware ou naive coerente
    now = datetime.now(UTC) if house_entry_time.tzinfo else datetime.now()
    steps[-1].duracao_dias = max(
        1, int((now - house_entry_time).total_seconds() / (24 * 3600))
    )

    return steps
