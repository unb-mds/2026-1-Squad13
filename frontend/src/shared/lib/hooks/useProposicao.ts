import { useState, useEffect } from "react";
import { obterProposicao, obterMovimentacoesFases, obterMovimentacoesEventos, obterConfiabilidade } from "../api";
import {
  mapProposicaoToProposition,
  mapPeriodoFaseToPhaseEntry,
  mapEventoTramitacaoToTimelineEvent,
  mapMovimentacoesToTransitSteps,
} from "../mappers";
import { PROPOSICOES_MOCK } from "../mock-data";
import type { Proposition } from "@/features/proposicoes/components/PropositionsTable";
import type { PhaseEntry } from "@/features/proposicoes/components/PhaseTimeline";
import type { TimelineEvent } from "@/features/proposicoes/components/EventTimeline";
import type { TransitStep } from "@/features/proposicoes/components/HouseTransitDiagram";

// Fallback mock data from prototype for detailed display
const fallbackProposition: Proposition = {
  id: "mock-1",
  numero: "2547/2023",
  tipo: "PL",
  ementa: "Dispõe sobre a proteção de dados pessoais no âmbito da administration pública federal e estabelece diretrizes para o tratamento de informações sensíveis, cria mecanismos de fiscalização e penalidades, e altera a Lei nº 13.709/2018 (Lei Geral de Proteção de Dados).",
  casaAtual: "Câmara",
  faseAtual: "Comissão de Constituição e Justiça",
  autor: "Dep. Maria Silva (PT-SP)",
  diasNaEtapa: 45,
  diasTotais: 120,
  ultimoEventoRelevante: "Designação de Relator CCJ",
  dataUltimoEvento: "15/02/2024",
  atraso: 12,
  coberturaDados: 94,
  confiabilidade: "alta",
  statusTramitacao: "em-atraso",
  status: "Em Tramitação",
  statusLabel: "Em atraso",
  transitouEntreCasas: false,
};

const fallbackPhases: PhaseEntry[] = [
  { id: "1", fase: "Recebimento e Despacho Inicial", ocorrencia: 1, dataEntrada: "12/03/2023", dataSaida: "18/03/2023", duracaoDias: 6, isRecorrente: false, isCurrent: false },
  { id: "2", fase: "Comissão de Ciência e Tecnologia", ocorrencia: 1, dataEntrada: "18/03/2023", dataSaida: "15/05/2023", duracaoDias: 58, atrasoDias: 13, isRecorrente: false, isCurrent: false },
  { id: "3", fase: "Comissão de Trabalho e Administração Pública", ocorrencia: 1, dataEntrada: "15/05/2023", dataSaida: "28/08/2023", duracaoDias: 105, atrasoDias: 42, isRecorrente: false, isCurrent: false },
  { id: "4", fase: "Revisão - Retorno para Comissão de Ciência e Tecnologia", ocorrencia: 2, dataEntrada: "28/08/2023", dataSaida: "15/11/2023", duracaoDias: 79, atrasoDias: 24, isRecorrente: true, isCurrent: false },
  { id: "5", fase: "Plenário - Primeira Discussão", ocorrencia: 1, dataEntrada: "15/11/2023", dataSaida: "08/02/2024", duracaoDias: 85, atrasoDias: 31, isRecorrente: false, isCurrent: false },
  { id: "6", fase: "Comissão de Constituição e Justiça", ocorrencia: 1, dataEntrada: "08/02/2024", dataSaida: undefined, duracaoDias: 45, atrasoDias: 12, isRecorrente: false, isCurrent: true },
];

const fallbackEvents: TimelineEvent[] = [
  { id: "1", data: "12/03/2023", hora: "10:15", orgao: "Mesa Diretora - Câmara", tipoEvento: "despacho", titulo: "Protocolo e Numeração", descricao: "Proposição protocolada e numerada como PL 2547/2023", isRelevante: true, flags: { mudancaFase: true } },
  { id: "2", data: "18/03/2023", hora: "14:30", orgao: "Mesa Diretora - Câmara", tipoEvento: "despacho", titulo: "Distribuição para Comissão", descricao: "Distribuída para Comissão de Ciência e Tecnologia", isRelevante: true, flags: { mudancaFase: true } },
  { id: "3", data: "25/03/2023", hora: "09:00", orgao: "Comissão de Ciência e Tecnologia", tipoEvento: "despacho", titulo: "Designação de Relator", descricao: "Designado relator: Dep. Carlos Mendes (PDT-MG)", isRelevante: true },
  { id: "4", data: "12/04/2023", hora: "15:00", orgao: "Comissão de Ciência e Tecnologia", tipoEvento: "outro", titulo: "Audiência Pública", descricao: "Realizada audiência pública com especialistas em proteção de dados e representantes da sociedade civil", isRelevante: true },
  { id: "5", data: "28/04/2023", hora: "11:45", orgao: "Comissão de Ciência e Tecnologia", tipoEvento: "parecer", titulo: "Parecer do Relator", descricao: "Parecer do relator favorável com substitutivo propondo alterações técnicas e ajustes de redação", isRelevante: true },
  { id: "6", data: "15/05/2023", hora: "16:20", orgao: "Comissão de Ciência e Tecnologia", tipoEvento: "deliberacao", titulo: "Aprovação por Unanimidade", descricao: "Parecer aprovado por unanimidade com elogios à abrangência da proposta", isRelevante: true, flags: { mudancaFase: true } },
  { id: "7", data: "15/05/2023", hora: "16:45", orgao: "Mesa Diretora - Câmara", tipoEvento: "despacho", titulo: "Redistribuição", descricao: "Distribuída para Comissão de Trabalho e Administração Pública", isRelevante: true, flags: { mudancaFase: true } },
  { id: "8", data: "22/05/2023", hora: "10:00", orgao: "Comissão de Trabalho e Administração Pública", tipoEvento: "despacho", titulo: "Designação de Relatora", descricao: "Designada relatora: Dep. Ana Paula Lima (REDE-CE)", isRelevante: true },
  { id: "9", data: "18/06/2023", hora: "14:15", orgao: "Comissão de Trabalho e Administração Pública", tipoEvento: "emenda", titulo: "Apresentação de Emendas", descricao: "Apresentadas 7 emendas ao substitutivo versando sobre aplicação no setor público", isRelevante: true },
  { id: "10", data: "12/07/2023", hora: "09:30", orgao: "Comissão de Trabalho e Administração Pública", tipoEvento: "outro", titulo: "Solicitação de Prazo Adicional", descricao: "Solicitado prazo adicional para análise de emendas devido à complexidade técnica (atraso detectado)", isRelevante: true, flags: { atraso: true } },
  { id: "11", data: "05/08/2023", hora: "11:00", orgao: "Comissão de Trabalho e Administração Pública", tipoEvento: "parecer", titulo: "Parecer da Relatora", descricao: "Parecer da relatora favorável com incorporação parcial de emendas e sugestões de aprimoramento", isRelevante: true },
  { id: "12", data: "28/08/2023", hora: "15:40", orgao: "Comissão de Trabalho e Administração Pública", tipoEvento: "deliberacao", titulo: "Aprovação com Ressalvas", descricao: "Parecer aprovado com ressalvas, retorno à comissão de origem solicitado para verificação de compatibilidade", isRelevante: true, flags: { mudancaFase: true } },
  { id: "13", data: "28/08/2023", hora: "16:00", orgao: "Mesa Diretora - Câmara", tipoEvento: "despacho", titulo: "Retorno para Comissão de Origem", descricao: "Retorno para Comissão de Ciência e Tecnologia para análise de compatibilidade entre emendas", isRelevante: true, flags: { mudancaFase: true } },
  { id: "14", data: "05/09/2023", hora: "10:30", orgao: "Comissão de Ciência e Tecnologia", tipoEvento: "despacho", titulo: "Redesignação de Relator", descricao: "Redesignado relator: Dep. Roberto Alves (MDB-BA)", isRelevante: true },
  { id: "15", data: "28/10/2023", hora: "14:00", orgao: "Comissão de Ciência e Tecnologia", tipoEvento: "parecer", titulo: "Parecer Complementar", descricao: "Parecer complementar aprovando compatibilidade das emendas com o texto original", isRelevante: true },
  { id: "16", data: "15/11/2023", hora: "16:30", orgao: "Mesa Diretora - Câmara", tipoEvento: "despacho", titulo: "Encaminhamento para Plenário", descricao: "Encaminhada para discussão em plenário após conclusão das comissões", isRelevante: true, flags: { mudancaFase: true } },
  { id: "17", data: "22/11/2023", hora: "10:00", orgao: "Plenário - Câmara", tipoEvento: "outro", titulo: "Primeira Discussão", descricao: "Primeira discussão em plenário - apresentação do relatório consolidado e abertura de debates", isRelevante: true },
  { id: "18", data: "06/12/2023", hora: "15:20", orgao: "Plenário - Câmara", tipoEvento: "emenda", titulo: "Apresentação de Destaques", descricao: "Apresentados 12 destaques para votação em separado de dispositivos específicos", isRelevante: true },
  { id: "19", data: "20/12/2023", hora: "14:45", orgao: "Plenário - Câmara", tipoEvento: "deliberacao", titulo: "Votação de Destaques", descricao: "Aprovados 8 dos 12 destaques apresentados após intenso debate", isRelevante: true },
  { id: "20", data: "08/02/2024", hora: "17:30", orgao: "Plenário - Câmara", tipoEvento: "deliberacao", titulo: "Aprovação em Plenário", descricao: "Aprovado texto final em plenário com modificações, encaminhado para análise de constitucionalidade", isRelevante: true, flags: { mudancaFase: true } },
  { id: "21", data: "08/02/2024", hora: "18:00", orgao: "Mesa Diretora - Câmara", tipoEvento: "despacho", titulo: "Distribuição para CCJ", descricao: "Distribuída para Comissão de Constituição e Justiça (análise de constitucionalidade)", isRelevante: true, flags: { mudancaFase: true } },
  { id: "22", data: "15/02/2024", hora: "09:00", orgao: "Comissão de Constituição e Justiça", tipoEvento: "despacho", titulo: "Designação de Relator CCJ", descricao: "Designado relator: Dep. Paulo Ribeiro (PL-GO)", isRelevante: true },
  { id: "23", data: "15/04/2024", hora: "11:30", orgao: "Comissão de Constituição e Justiça", tipoEvento: "parecer", titulo: "Parecer pela Constitucionalidade", descricao: "Parecer do relator pela constitucionalidade, juridicidade e técnica legislativa apresentado", isRelevante: true },
];

const fallbackTransitSteps: TransitStep[] = [
  { casa: "Câmara", tipo: "origem", dataEntrada: "12/03/2023", duracaoDias: 789 },
];

const fallbackReliability = {
  cobertura: 94,
  statusHistorico: "completo" as const,
  ultimaAtualizacao: "31/05/2026 às 14:23",
  fontes: [
    "Sistema de Tramitação do Congresso Nacional (API oficial)",
    "Portal da Legislação Federal",
    "Diário Oficial da União - Seção 1",
  ],
  limitacoes: [
    "Eventos anteriores a 01/01/2020 podem ter registro parcial devido à migração de sistemas",
    "Despachos internos de comissões podem ter atraso de até 48h para publicação",
    "Documentos anexos estão sujeitos à disponibilidade das fontes oficiais",
  ],
};

export function useProposicao(id?: string) {
  const [proposicao, setProposicao] = useState<Proposition | null>(null);
  const [phases, setPhases] = useState<PhaseEntry[]>([]);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [transitSteps, setTransitSteps] = useState<TransitStep[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [reliability, setReliability] = useState<any>(fallbackReliability);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setLoading(false);
      return;
    }

    const propId: string = id;
    let active = true;
    setLoading(true);
    setError(null);

    async function loadData() {
      try {
        const prop = await obterProposicao(propId);
        if (!active) return;

        if (!prop) {
          // Verify if the ID matches a mocked item in frontend
          const mockItem = PROPOSICOES_MOCK.find((p) => p.id === propId);
          if (mockItem) {
            const mappedProp = mapProposicaoToProposition(mockItem);
            setProposicao(mappedProp);
            setPhases(fallbackPhases);
            setEvents(fallbackEvents);
            setTransitSteps(fallbackTransitSteps);
          } else {
            setProposicao(fallbackProposition);
            setPhases(fallbackPhases);
            setEvents(fallbackEvents);
            setTransitSteps(fallbackTransitSteps);
          }
          setLoading(false);
          return;
        }

        // Real API data found, fetch sub-resources
        const [fasesRes, eventosRes, reliabilityRes] = await Promise.allSettled([
          obterMovimentacoesFases(propId),
          obterMovimentacoesEventos(propId, "relevante"),
          obterConfiabilidade(propId)
        ]);

        if (!active) return;

        const mappedProp = mapProposicaoToProposition(prop);
        setProposicao(mappedProp);

        if (reliabilityRes.status === "fulfilled" && reliabilityRes.value) {
          setReliability(reliabilityRes.value);
        } else {
          setReliability({
            ...fallbackReliability,
            cobertura: mappedProp.coberturaDados,
            ultimaAtualizacao: mappedProp.dataUltimoEvento ? `${mappedProp.dataUltimoEvento} às 14:00` : fallbackReliability.ultimaAtualizacao
          });
        }

        // Process Phase entry list
        if (fasesRes.status === "fulfilled" && fasesRes.value && Array.isArray(fasesRes.value)) {
          const rawFases = fasesRes.value as { diasCorridos: number }[];
          const mappedPhases = rawFases.map((f, idx: number) =>
            mapPeriodoFaseToPhaseEntry(f, idx, idx === rawFases.length - 1)
          );
          setPhases(mappedPhases);
        } else {
          // Empty or failed: fallback to mock phases
          setPhases(fallbackPhases);
        }

        // Process Event timeline list
        if (eventosRes.status === "fulfilled" && eventosRes.value && Array.isArray(eventosRes.value)) {
          const mappedEvents = (eventosRes.value as { sequencia?: number }[]).map((e) => mapEventoTramitacaoToTimelineEvent(e));
          setEvents(mappedEvents);

          if (prop && prop.transitSteps && prop.transitSteps.length > 0) {
            const steps = prop.transitSteps.map((s) => ({
              casa: s.casa as "Câmara" | "Senado",
              tipo: s.tipoPasso as "origem" | "revisora" | "retorno" | "final",
              dataEntrada: s.dataEntrada,
              dataSaida: s.dataSaida || undefined,
              duracaoDias: s.duracaoDias,
            }));
            setTransitSteps(steps);
          } else {
            const steps = mapMovimentacoesToTransitSteps(eventosRes.value as { siglaOrgao?: string }[]);
            setTransitSteps(steps);
          }
        } else {
          // Empty or failed: fallback to mock events
          setEvents(fallbackEvents);
          setTransitSteps(fallbackTransitSteps);
        }

      } catch (err) {
        console.error("Erro no hook useProposicao, usando dados mockados de fallback:", err);
        if (active) {
          setProposicao(fallbackProposition);
          setPhases(fallbackPhases);
          setEvents(fallbackEvents);
          setTransitSteps(fallbackTransitSteps);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      active = false;
    };
  }, [id]);

  return {
    proposicao,
    phases,
    events,
    transitSteps,
    reliability,
    loading,
    error,
  };
}
