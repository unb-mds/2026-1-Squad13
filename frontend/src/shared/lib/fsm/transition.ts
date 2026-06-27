import type { FSMState, InputType, House, StepRole } from "./types";

export function transition(state: FSMState, input: InputType, eventTimestamp: number): FSMState {
  let proximaCasa: House = state.casaAtiva;
  let gatilhoFoiImplicito = false;

  // Regras de Transição da Máquina de Estados
  if (state.casaAtiva === "Câmara") {
    if (input === "GATILHO_REMESSA") {
      proximaCasa = "Senado";
      gatilhoFoiImplicito = false;
    } else if (input === "EXCLUSIVO_SENADO") {
      // Invariante 5: Auto-correção por gatilho implícito única por fronteira temporal
      if (!state.ultimoGatilhoFoiImplicito) {
        proximaCasa = "Senado";
        gatilhoFoiImplicito = true;
      }
    }
  } else { // Senado
    if (input === "GATILHO_RETORNO" || input === "GATILHO_REMESSA") {
      proximaCasa = "Câmara";
      gatilhoFoiImplicito = false;
    } else if (input === "EXCLUSIVO_CÂMARA") {
      // Invariante 5: Auto-correção implícita anti-ping-pong
      if (!state.ultimoGatilhoFoiImplicito) {
        proximaCasa = "Câmara";
        gatilhoFoiImplicito = true;
      }
    }
  }

  // Atualização da última Casa com certeza absoluta (Invariante 4)
  const novaCerteza = (input === "EXCLUSIVO_CÂMARA" || input === "EXCLUSIVO_SENADO")
    ? proximaCasa
    : state.ultimaCasaNaoAmbigua;

  // Estado de controle para saber se o projeto já passou pela revisora
  const proximoJaPassouRevisora = state.jaPassouPelaRevisora || (proximaCasa !== state.casaOrigem);

  // Invariante 8: Determinação de papel por percurso semântico puro (sem timestamps)
  let novoTipo: StepRole = "origem";
  if (proximaCasa !== state.casaOrigem) {
    novoTipo = "revisora";
  } else if (proximoJaPassouRevisora) {
    novoTipo = "retorno";
  }

  const mudouDeCasa = proximaCasa !== state.casaAtiva;

  return {
    casaAtiva: proximaCasa,
    tipoPasso: novoTipo,
    timestampEntrada: mudouDeCasa ? eventTimestamp : state.timestampEntrada,
    dataEntradaStr: state.dataEntradaStr, // Será atualizada por build.ts
    casaOrigem: state.casaOrigem,
    ultimaCasaNaoAmbigua: novaCerteza,
    jaPassouPelaRevisora: proximoJaPassouRevisora,
    ultimoGatilhoFoiImplicito: mudouDeCasa ? gatilhoFoiImplicito : state.ultimoGatilhoFoiImplicito
  };
}
