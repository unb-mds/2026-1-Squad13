import type { RawEvent, InputType } from "./types";

const PADROES_REMESSA = [
  /(remessa|remetido|envio|ofício.*encaminhando.*autógrafo).*senado/i,
  /remessa ao senado federal/i
];

const PADROES_RETORNO_SENADO = [
  /^(remetida|remessa)[\s\S]*câmara/i,
  /^(ofício|comunicação)[\s\S]*câmara/i
];

const PADROES_RETORNO_CAMARA = [
  /^(recebido\s+o\s+ofício|recebimento\s+do\s+ofício|recebido)[\s\S]*senado/i,
  /^retorno[\s\S]*senado/i
];

const SIGLAS_EXCLUSIVAS_SENADO = [
  "ccj", "cae", "cas", "cra", "cre", "ci", "cdh", "cma", 
  "csp", "ctfc", "cdr", "sexpe", "ssclsf", "slsf", "seadi", 
  "sacdh", "sace", "saccj", "sacas", "sacae", "sacma", 
  "sacsp", "sacra", "sacifr", "sacct", "sacdr", "sactfc"
];

const SIGLAS_EXCLUSIVAS_CAMARA = [
  "ccjc", "cft", "ccjr", "ccp", "cpasf", "csaude", "cult", "ctrab", "cde", "cvt", "cidoso"
];

export function classifyEvent(event: RawEvent): InputType {
  const desc = event.descricaoOriginal || event.descricao || "";
  const sigla = (event.siglaOrgao || "").toLowerCase().trim();
  const orgaoLower = (event.orgao || "").toLowerCase();

  // 1. Verificar gatilhos explícitos
  if (event.remessaOuRetorno === "REMESSA") {
    return "GATILHO_REMESSA";
  }
  if (event.remessaOuRetorno === "RETORNO") {
    return "GATILHO_RETORNO";
  }

  // Regexes para remessa
  for (const pattern of PADROES_REMESSA) {
    if (pattern.test(desc)) {
      return "GATILHO_REMESSA";
    }
  }

  // Regexes para retorno
  for (const pattern of PADROES_RETORNO_SENADO) {
    if (pattern.test(desc)) {
      return "GATILHO_RETORNO";
    }
  }
  for (const pattern of PADROES_RETORNO_CAMARA) {
    if (pattern.test(desc)) {
      return "GATILHO_RETORNO";
    }
  }

  // 2. Localidades exclusivas
  // Evitar correspondência de substring frouxa como sigla.includes("sf") que casa com "cpasf"
  const eExclusivoSenado = 
    sigla === "sf" || 
    sigla === "slsf" || 
    sigla === "ssclsf" || 
    orgaoLower.includes("sf") || 
    orgaoLower.includes("senado") || 
    SIGLAS_EXCLUSIVAS_SENADO.includes(sigla);

  if (eExclusivoSenado) {
    return "EXCLUSIVO_SENADO";
  }

  if (
    SIGLAS_EXCLUSIVAS_CAMARA.includes(sigla) || 
    (sigla.length >= 4 && sigla.startsWith("c") && !sigla.startsWith("sa"))
  ) {
    return "EXCLUSIVO_CÂMARA";
  }

  return "AMBÍGUO_OU_NEUTRO";
}
