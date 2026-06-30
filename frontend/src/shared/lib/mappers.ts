import type { Proposicao, StatusProposicao } from '../types';
import type { Proposition } from '@/features/proposicoes/components/PropositionsTable';
import type { PhaseEntry } from '@/features/proposicoes/components/PhaseTimeline';
import type { TimelineEvent } from '@/features/proposicoes/components/EventTimeline';
import type { TransitStep } from '@/features/proposicoes/components/HouseTransitDiagram';

// Converte data ISO ou string em formato DD/MM/AAAA
export function formatarDataBr(dataStr?: string): string {
  if (!dataStr) return '';
  const cleanStr = dataStr.replace(/Z$/i, '');
  
  // Se for apenas data no formato YYYY-MM-DD, formata diretamente para evitar timezone-shift
  const match = cleanStr.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (match) {
    return `${match[3]}/${match[2]}/${match[1]}`;
  }

  try {
    const data = new Date(cleanStr);
    if (isNaN(data.getTime())) {
      // Tenta fazer split simples se for yyyy-mm-dd
      const parts = cleanStr.split('T')[0].split('-');
      if (parts.length === 3) {
        return `${parts[2]}/${parts[1]}/${parts[0]}`;
      }
      return dataStr;
    }
    return data.toLocaleDateString('pt-BR');
  } catch {
    return dataStr || '';
  }
}

export function normalizarStatus(statusRaw?: string): StatusProposicao {
  if (!statusRaw) return 'Em Tramitação';
  
  const statusTrim = statusRaw.trim();
  if (['Em Tramitação', 'Em Pauta', 'Aprovada', 'Sancionada', 'Vetada', 'Arquivada'].includes(statusTrim)) {
    return statusTrim as StatusProposicao;
  }

  const raw = statusRaw.toUpperCase();

  if (raw.includes("NORMA JURÍDICA") || raw.includes("SANCIONAD") || raw.includes("CONCLUÍDA")) {
    return "Sancionada";
  }

  if (raw.includes("VETAD")) {
    return "Vetada";
  }

  if (
    raw.includes("REJEITAD") ||
    raw.includes("ARQUIVAD") ||
    raw.includes("PREJUDICAD") ||
    raw.includes("RETIRAD") ||
    raw.includes("APENSAD")
  ) {
    return "Arquivada";
  }

  if (raw.includes("APROVAD")) {
    return "Aprovada";
  }

  if (raw.includes("PAUTA") || raw.includes("AGUARDANDO")) {
    return "Em Pauta";
  }

  return "Em Tramitação";
}

export function mapProposicaoToProposition(p: Proposicao): Proposition {
  // Calcula os dias na etapa atual a partir da data de última movimentação
  let diasNaEtapa = 0;
  if (p.dataUltimaMovimentacao) {
    const diffTime = Math.abs(Date.now() - new Date(p.dataUltimaMovimentacao).getTime());
    diasNaEtapa = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  }

  // Determina a casa atual
  let casaAtual: "Câmara" | "Senado" | "Sanção" = "Câmara";
  if (p.status === "Sancionada" || p.status === "Vetada") {
    casaAtual = "Sanção";
  } else if (p.orgaoOrigem?.toLowerCase().includes("senado") || p.orgaoAtual?.toLowerCase().includes("sf") || p.orgaoAtual?.toLowerCase().includes("senado")) {
    casaAtual = "Senado";
  }

  // Determina o status de tramitação para a UI (categorização por cores)
  let statusTramitacao: Proposition["statusTramitacao"] = "em-tramitacao";
  
  if (p.temAtraso) {
    statusTramitacao = "em-atraso";
  } else {
    const statusLower = p.status.toLowerCase();
    
    if (
      statusLower.includes("aprovada") || 
      statusLower.includes("sancionada") || 
      statusLower.includes("concluída")
    ) {
      statusTramitacao = "aprovada";
    } else if (
      statusLower.includes("rejeitada") || 
      statusLower.includes("arquivada") || 
      statusLower.includes("vetada")
    ) {
      statusTramitacao = "arquivada";
    } else if (
      statusLower.includes("aguardando") || 
      statusLower.includes("pauta")
    ) {
      statusTramitacao = "aguardando";
    }
  }

  const statusCanonico = normalizarStatus(p.status);

  return {
    id: p.codigoNormalizado || p.id,
    numero: `${p.numero}/${p.ano}`,
    tipo: p.tipo,
    ementa: p.ementaResumida || p.ementa,
    casaAtual,
    faseAtual: p.orgaoAtual || "Protocolo",
    diasNaEtapa: diasNaEtapa || 0,
    diasTotais: p.tempoTotalDias || 0,
    ultimoEventoRelevante: p.statusOriginal || p.status || "Movimentação registrada",
    dataUltimoEvento: formatarDataBr(p.dataUltimaMovimentacao),
    autor: p.autor,
    atraso: p.temAtraso ? Math.max(0, p.tempoTotalDias - 180) : 0,
    coberturaDados: p.coberturaDados,
    confiabilidade: p.confiabilidade,
    statusTramitacao,
    status: statusCanonico,
    statusLabel: p.temAtraso ? "Em atraso" : statusCanonico,
    transitouEntreCasas: p.orgaoOrigem?.toLowerCase().includes("senado") && p.orgaoAtual?.toLowerCase().includes("camara") || p.orgaoOrigem?.toLowerCase().includes("camara") && p.orgaoAtual?.toLowerCase().includes("senado"),
    tempoPorFase: p.tempoPorFase,
  };
}

// Converte PeriodoFaseResponse do backend para PhaseEntry do protótipo
export function mapPeriodoFaseToPhaseEntry(p: { 
  faseNome?: string; 
  faseCodigo?: string; 
  ocorrencia?: number; 
  dataEntrada?: string; 
  dataSaida?: string; 
  diasCorridos: number;
  motivoTravamento?: string | null;
  numeroTurno?: number | null;
  subtipoFase?: string | null;
}, index: number, isLast: boolean): PhaseEntry {
  return {
    id: String(index + 1),
    fase: p.faseNome || p.faseCodigo || "N/A",
    ocorrencia: p.ocorrencia || 1,
    dataEntrada: formatarDataBr(p.dataEntrada),
    dataSaida: p.dataSaida ? formatarDataBr(p.dataSaida) : undefined,
    duracaoDias: p.diasCorridos || 0,
    atrasoDias: p.diasCorridos > 45 ? p.diasCorridos - 45 : 0, // Mediana estimada em 45 dias
    isRecorrente: (p.ocorrencia || 1) > 1,
    isCurrent: isLast,
    motivoTravamento: p.motivoTravamento || undefined,
    numeroTurno: p.numeroTurno !== null ? p.numeroTurno : undefined,
    subtipoFase: p.subtipoFase || undefined,
  };
}

// Converte EventoResponse do backend para TimelineEvent do protótipo
export function mapEventoTramitacaoToTimelineEvent(e: {
  sequencia?: number;
  dataEvento?: string;
  siglaOrgao?: string;
  tipoEvento?: string;
  descricaoOriginal?: string;
  relevante?: boolean;
  mudouFase?: boolean;
  temAtraso?: boolean;
  remessaOuRetorno?: boolean;
}): TimelineEvent {
  let tipoEvento: TimelineEvent["tipoEvento"] = "outro";
  const backendTipo = e.tipoEvento?.toLowerCase() || "";

  if (backendTipo.includes("apresentacao")) tipoEvento = "mudanca-fase";
  else if (backendTipo.includes("votacao") || backendTipo.includes("deliberacao") || backendTipo.includes("aprovacao") || backendTipo.includes("rejeicao")) tipoEvento = "deliberacao";
  else if (backendTipo.includes("apensamento") || backendTipo.includes("apensacao")) tipoEvento = "apensamento";
  else if (backendTipo.includes("remessa") || backendTipo.includes("recebimento")) tipoEvento = "transicao-casa";
  else if (backendTipo.includes("despacho")) tipoEvento = "despacho";
  else if (backendTipo.includes("parecer")) tipoEvento = "parecer";
  else if (backendTipo.includes("emenda")) tipoEvento = "emenda";

  return {
    id: String(e.sequencia || Math.random()),
    data: formatarDataBr(e.dataEvento),
    hora: e.dataEvento?.includes("T") ? e.dataEvento.split("T")[1].substring(0, 5) : undefined,
    orgao: e.siglaOrgao || "N/A",
    tipoEvento,
    titulo: e.descricaoOriginal ? (e.descricaoOriginal.length > 50 ? e.descricaoOriginal.substring(0, 47) + "..." : e.descricaoOriginal) : "Movimentação registrada",
    descricao: e.descricaoOriginal || "",
    isRelevante: e.relevante || false,
    flags: {
      mudancaFase: e.mudouFase || false,
      atraso: e.temAtraso || false,
      transitoCasas: !!e.remessaOuRetorno,
      apensamento: e.descricaoOriginal?.toLowerCase().includes("apensado") || false,
    },
  };
}

export function identificarCasaDoEvento(
  siglaOrgao?: string,
  orgao?: string,
  proposicaoId?: string,
  remessaOuRetorno?: string | null,
  casaOrigem?: "Câmara" | "Senado"
): "Câmara" | "Senado" {
  if (remessaOuRetorno === "REMESSA") {
    return casaOrigem === "Câmara" ? "Senado" : "Câmara";
  }
  if (remessaOuRetorno === "RETORNO") {
    return casaOrigem || "Câmara";
  }

  const sigla = siglaOrgao?.toLowerCase() || "";
  const orgaoLower = orgao?.toLowerCase() || "";

  // 1. Heurísticas baseadas em siglas de órgãos ou termos explícitos
  if (
    sigla.includes("sf") || 
    orgaoLower.includes("sf") || 
    orgaoLower.includes("senado") || 
    ["ccj", "cae", "cas", "cra", "cre", "ci", "cdh", "ce", "cma", "csp", "ctfc", "cdr", "sexpe", "ssclsf"].includes(sigla)
  ) {
    return "Senado";
  }

  if (
    ["ccjc", "cft", "ccjr", "mesa", "plen", "ccp"].includes(sigla) || 
    (sigla.length >= 4 && sigla.startsWith("c"))
  ) {
    return "Câmara";
  }

  // 2. Prefixo do ID como fallback caso a sigla seja inconclusiva
  if (proposicaoId?.startsWith("senado:")) return "Senado";
  if (proposicaoId?.startsWith("camara:")) return "Câmara";

  // 3. Fallback final
  return casaOrigem || "Câmara";
}

export function mapMovimentacoesToTransitSteps(movs: {
  proposicaoId?: string;
  siglaOrgao?: string;
  orgao?: string;
  data?: string;
  dataEvento?: string;
  descricaoOriginal?: string;
  remessaOuRetorno?: string | null;
}[]): TransitStep[] {
  if (movs.length === 0) {
    return [
      { casa: "Câmara", tipo: "origem", dataEntrada: "Apresentação", duracaoDias: 0 }
    ];
  }

  const firstMov = movs[0];
  const casaOrigem = identificarCasaDoEvento(
    firstMov.siglaOrgao,
    firstMov.orgao,
    firstMov.proposicaoId,
    firstMov.remessaOuRetorno
  );

  return [
    {
      casa: casaOrigem as "Câmara" | "Senado",
      tipo: "origem",
      dataEntrada: firstMov.dataEvento ? formatarDataBr(firstMov.dataEvento) : "Apresentação",
      duracaoDias: 0
    }
  ];
}
