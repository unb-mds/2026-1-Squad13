export type House = "Câmara" | "Senado";
export type StepRole = "origem" | "revisora" | "retorno";

export type InputType =
  | "GATILHO_REMESSA"
  | "GATILHO_RETORNO"
  | "EXCLUSIVO_CÂMARA"
  | "EXCLUSIVO_SENADO"
  | "AMBÍGUO_OU_NEUTRO";

export interface RawEvent {
  proposicaoId?: string;
  siglaOrgao?: string;
  orgao?: string;
  dataEvento?: string;
  data?: string;
  descricaoOriginal?: string;
  descricao?: string;
  remessaOuRetorno?: string | null;
}

export interface FSMState {
  casaAtiva: House;
  tipoPasso: StepRole;
  timestampEntrada: number;
  dataEntradaStr: string;
  casaOrigem: House;
  ultimaCasaNaoAmbigua: House;
  jaPassouPelaRevisora: boolean;
  ultimoGatilhoFoiImplicito: boolean;
}
