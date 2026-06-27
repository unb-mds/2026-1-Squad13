import type { RawEvent, FSMState, House } from "./types";
import { classifyEvent } from "./classify";
import { transition } from "./transition";
import { formatarDataBr } from "../mappers";
import type { TransitStep } from "@/features/proposicoes/components/HouseTransitDiagram";

export function buildTransitSteps(events: RawEvent[], casaOrigem: House): TransitStep[] {
  if (events.length === 0) {
    return [
      { casa: casaOrigem, tipo: "origem", dataEntrada: "Apresentação", duracaoDias: 0 }
    ];
  }

  // Ordena cronologicamente por timestamp
  const parseTime = (s?: string) => {
    if (!s) return 0;
    // Limpa timezone shift
    const clean = s.replace(/Z$/i, "");
    return new Date(clean).getTime();
  };

  const sortedEvents = [...events].sort((a, b) => {
    return parseTime(a.dataEvento || a.data) - parseTime(b.dataEvento || b.data);
  });

  const firstEvent = sortedEvents[0];
  const firstEventTime = parseTime(firstEvent.dataEvento || firstEvent.data);

  // Inicializa o Estado (Invariante 2)
  let state: FSMState = {
    casaAtiva: casaOrigem,
    tipoPasso: "origem",
    timestampEntrada: firstEventTime,
    dataEntradaStr: formatarDataBr(firstEvent.dataEvento || firstEvent.data),
    casaOrigem: casaOrigem,
    ultimaCasaNaoAmbigua: casaOrigem,
    jaPassouPelaRevisora: false,
    ultimoGatilhoFoiImplicito: false
  };

  const steps: TransitStep[] = [];
  
  // Adiciona o passo inicial
  steps.push({
    casa: state.casaAtiva,
    tipo: state.tipoPasso,
    dataEntrada: state.dataEntradaStr,
    duracaoDias: 0
  });

  let houseEntryTime = firstEventTime;

  for (let i = 1; i < sortedEvents.length; i++) {
    const ev = sortedEvents[i];
    const evTime = parseTime(ev.dataEvento || ev.data);
    const input = classifyEvent(ev);
    
    const nextState = transition(state, input, evTime);

    // Invariante 7: Correspondência biunívoca (Novo TransitStep sse casa mudou)
    if (nextState.casaAtiva !== state.casaAtiva) {
      const dataMudaStr = formatarDataBr(ev.dataEvento || ev.data);
      
      // Fecha o passo anterior
      steps[steps.length - 1].dataSaida = dataMudaStr;
      steps[steps.length - 1].duracaoDias = Math.max(
        1,
        Math.floor((evTime - houseEntryTime) / (1000 * 60 * 60 * 24))
      );

      // Inicia novo passo
      steps.push({
        casa: nextState.casaAtiva,
        tipo: nextState.tipoPasso,
        dataEntrada: dataMudaStr,
        duracaoDias: 0
      });

      houseEntryTime = evTime;
    }

    state = nextState;
  }

  // Duração do último passo (até hoje)
  const lastTime = Date.now();
  steps[steps.length - 1].duracaoDias = Math.max(
    1,
    Math.floor((lastTime - houseEntryTime) / (1000 * 60 * 60 * 24))
  );

  return steps;
}
