import { useState, useEffect } from "react";
import {
  obterMetricas,
  obterDadosStatus,
  obterGargalos,
  obterComparacaoTemas,
  obterTempoPorFase,
  obterEvolucaoTemporal,
  obterTransicoesCasas,
  obterEstoque,
  obterHandoff,
  obterCobertura,
  obterQualidade,
} from "../api";
import type {
  FiltrosProposicao,
  MetricasDashboard,
  DashboardEstoqueResponse,
  DashboardHandoffResponse,
  CoberturaMetricaResponse,
  DashboardQualidadeResponse,
} from "../../types";

// Mock data fallbacks from prototype
const defaultPipelineData = [
  { name: "Recebimento e Despacho", count: 142, percentage: 100, medianDays: 8 },
  { name: "Comissão Temática - Análise", count: 98, percentage: 69, medianDays: 45 },
  { name: "Comissão de Constituição e Justiça", count: 76, percentage: 53.5, medianDays: 62 },
  { name: "Plenário - Discussão e Votação", count: 45, percentage: 31.7, medianDays: 38 },
  { name: "Revisão na Casa Revisora", count: 32, percentage: 22.5, medianDays: 71 },
  { name: "Revisão - Comissões", count: 21, percentage: 14.8, medianDays: 54 },
  { name: "Revisão - Redação Final", count: 12, percentage: 8.5, medianDays: 15 },
  { name: "Sanção e Publicação", count: 8, percentage: 5.6, medianDays: 12 },
];

const defaultTimeSeriesData = [
  { mes: "Nov/25", entradas: 24, saidas: 18 },
  { mes: "Dez/25", entradas: 31, saidas: 22 },
  { mes: "Jan/26", entradas: 28, saidas: 25 },
  { mes: "Fev/26", entradas: 35, saidas: 29 },
  { mes: "Mar/26", entradas: 42, saidas: 31 },
  { mes: "Abr/26", entradas: 38, saidas: 34 },
  { mes: "Mai/26", entradas: 45, saidas: 28 },
];

const defaultBottleneckData = {
  porOrgao: [
    { nome: "Comissão de Constituição e Justiça - Câmara", proposicoes: 34, tempoMediano: 87, rank: 1 },
    { nome: "Comissão de Finanças e Tributação - Senado", proposicoes: 28, tempoMediano: 79, rank: 2 },
    { nome: "Comissão de Assuntos Econômicos - Senado", proposicoes: 22, tempoMediano: 71, rank: 3 },
    { nome: "Comissão de Educação - Câmara", proposicoes: 18, tempoMediano: 58, rank: 4 },
    { nome: "Mesa Diretora - Câmara", proposicoes: 31, tempoMediano: 45, rank: 5 },
  ],
  porFase: [
    { nome: "Revisão na Casa Revisora", proposicoes: 32, tempoMediano: 71, rank: 1 },
    { nome: "Comissão de Constituição e Justiça", proposicoes: 76, tempoMediano: 62, rank: 2 },
    { nome: "Revisão - Comissões", proposicoes: 21, tempoMediano: 54, rank: 3 },
    { nome: "Comissão Temática - Análise", proposicoes: 98, tempoMediano: 45, rank: 4 },
    { nome: "Plenário - Discussão e Votação", proposicoes: 45, tempoMediano: 38, rank: 5 },
  ],
  porTema: [
    { nome: "Reforma Tributária", proposicoes: 12, tempoMediano: 95, rank: 1 },
    { nome: "Direitos Digitais e Proteção de Dados", proposicoes: 18, tempoMediano: 73, rank: 2 },
    { nome: "Infraestrutura e Concessões", proposicoes: 15, tempoMediano: 68, rank: 3 },
    { nome: "Educação e Cultura", proposicoes: 24, tempoMediano: 52, rank: 4 },
    { nome: "Meio Ambiente e Sustentabilidade", proposicoes: 21, tempoMediano: 47, rank: 5 },
  ],
};

const defaultHouseTransitionData = {
  transitions: [
    { origem: "Câmara" as const, destino: "Senado" as const, quantidade: 18, tempoMedioTransicao: 7 },
    { origem: "Senado" as const, destino: "Câmara" as const, quantidade: 12, tempoMedioTransicao: 9 },
  ],
  totalCamara: 847,
  totalSenado: 576,
};

const defaultEstoqueData: DashboardEstoqueResponse = {
  ativo: [
    { codigo: "PROTOCOLO_INICIAL", nome: "Protocolo inicial", natureza: "operacional", permiteEstoqueAtual: true, total: 142 },
    { codigo: "ANALISE_COMISSOES", nome: "Análise em comissões", natureza: "operacional", permiteEstoqueAtual: true, total: 98 },
    { codigo: "AGUARDANDO_PAUTA", nome: "Aguardando pauta", natureza: "operacional", permiteEstoqueAtual: true, total: 45 },
  ],
  passivo: [
    { codigo: "ENCERRADA", nome: "Encerrada", natureza: "terminal", permiteEstoqueAtual: false, total: 847 },
  ]
};

export function useDashboard(filtros: FiltrosProposicao) {
  const [metricas, setMetricas] = useState<MetricasDashboard | null>(null);
  const [pipelineData, setPipelineData] = useState<unknown[]>(defaultPipelineData);
  const [timeSeriesData, setTimeSeriesData] = useState<unknown[]>(defaultTimeSeriesData);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [bottleneckData, setBottleneckData] = useState<any>(defaultBottleneckData); // Mantendo any por ser objeto complexo mockado
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [houseTransitionData, setHouseTransitionData] = useState<any>(defaultHouseTransitionData);
  
  const [estoqueData, setEstoqueData] = useState<DashboardEstoqueResponse | null>(null);
  const [handoffData, setHandoffData] = useState<DashboardHandoffResponse | null>(null);
  const [coberturaData, setCoberturaData] = useState<CoberturaMetricaResponse[]>([]);
  const [qualidadeData, setQualidadeData] = useState<DashboardQualidadeResponse | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    async function loadData() {
      try {
        console.log("Dashboard: Iniciando carregamento de dados com filtros:", filtros);
        const [
          metricasRes,
          tempoFaseRes,
          gargalosRes,
          temasRes,
          statusRes,
          evolucaoRes,
          transicoesRes,
          estoqueRes,
          handoffRes,
          coberturaRes,
          qualidadeRes
        ] = await Promise.allSettled([
          obterMetricas(filtros),
          obterTempoPorFase(filtros),
          obterGargalos(filtros),
          obterComparacaoTemas(filtros),
          obterDadosStatus(filtros),
          obterEvolucaoTemporal(filtros),
          obterTransicoesCasas(filtros),
          obterEstoque(filtros),
          obterHandoff(filtros),
          obterCobertura(),
          obterQualidade(filtros)
        ]);

        if (!active) return;

        // 1. KPIs
        if (metricasRes.status === "fulfilled" && metricasRes.value) {
          setMetricas(metricasRes.value);
        }

        // 2. Pipeline Stages (tempo-por-fase)
        if (tempoFaseRes.status === "fulfilled" && tempoFaseRes.value.length > 0) {
          const maxCount = Math.max(...tempoFaseRes.value.map(f => f.quantidadeProposicoes), 1);
          const mappedPipeline = tempoFaseRes.value
            .sort((a, b) => a.ordemLogica - b.ordemLogica)
            .map(f => ({
              name: f.fase,
              count: f.quantidadeProposicoes,
              percentage: (f.quantidadeProposicoes / maxCount) * 100,
              medianDays: f.tempoMedioDias
            }));
          setPipelineData(mappedPipeline);
        } else {
          const temFiltroAtivo = !!(
            filtros.busca ||
            filtros.tipo ||
            filtros.status ||
            filtros.orgaoOrigem ||
            filtros.dataInicio ||
            filtros.dataFim
          );
          setPipelineData(temFiltroAtivo ? [] : defaultPipelineData);
        }

        // 3. Gargalos (por orgao, fase, tema)
        let mappedOrgao = defaultBottleneckData.porOrgao;
        if (gargalosRes.status === "fulfilled" && gargalosRes.value.length > 0) {
          mappedOrgao = gargalosRes.value.map((g, idx) => ({
            nome: g.orgao,
            proposicoes: g.quantidadeProposicoes,
            tempoMediano: Math.round(g.tempoMedioMeses * 30), // Converte meses para dias
            rank: idx + 1
          })).slice(0, 5);
        }

        let mappedTema = defaultBottleneckData.porTema;
        if (temasRes.status === "fulfilled" && temasRes.value.length > 0) {
          mappedTema = temasRes.value.map((t, idx) => ({
            nome: t.tema,
            proposicoes: 10 + idx, // Estimado se ausente
            tempoMediano: t.tempoMedioDias,
            rank: idx + 1
          })).slice(0, 5);
        }

        // Fases
        const mappedFase = defaultBottleneckData.porFase;

        setBottleneckData({
          porOrgao: mappedOrgao,
          porFase: mappedFase,
          porTema: mappedTema
        });

        // 4. House Transitions
        let totalCamara = defaultHouseTransitionData.totalCamara;
        let totalSenado = defaultHouseTransitionData.totalSenado;

        if (statusRes.status === "fulfilled" && statusRes.value.length > 0) {
          totalCamara = metricasRes.status === "fulfilled" ? Math.round(metricasRes.value.totalEmTramitacao * 0.6) : totalCamara;
          totalSenado = metricasRes.status === "fulfilled" ? Math.round(metricasRes.value.totalEmTramitacao * 0.4) : totalSenado;
        }

        if (transicoesRes.status === "fulfilled" && transicoesRes.value) {
          setHouseTransitionData(transicoesRes.value);
        } else {
          setHouseTransitionData({
            transitions: defaultHouseTransitionData.transitions,
            totalCamara,
            totalSenado
          });
        }

        // 5. Evolução temporal
        if (evolucaoRes.status === "fulfilled" && evolucaoRes.value && evolucaoRes.value.length > 0) {
          setTimeSeriesData(evolucaoRes.value);
        } else {
          setTimeSeriesData(defaultTimeSeriesData);
        }

        // 6. Novos Dados de Analíticos
        if (estoqueRes.status === "fulfilled" && estoqueRes.value) {
          console.log("Dashboard: Dados de estoque carregados com sucesso:", estoqueRes.value);
          setEstoqueData(estoqueRes.value);
        } else {
          console.warn("Dashboard: Falha ao carregar estoque ou sem dados:", estoqueRes.status);
          const temFiltroAtivo = !!(
            filtros.busca ||
            filtros.tipo ||
            filtros.status ||
            filtros.orgaoOrigem
          );
          setEstoqueData(temFiltroAtivo ? { ativo: [], passivo: [] } : defaultEstoqueData);
        }

        if (handoffRes.status === "fulfilled" && handoffRes.value) {
          setHandoffData(handoffRes.value);
        }
        if (coberturaRes.status === "fulfilled" && coberturaRes.value) {
          setCoberturaData(coberturaRes.value);
        }
        if (qualidadeRes.status === "fulfilled" && qualidadeRes.value) {
          setQualidadeData(qualidadeRes.value);
        }

      } catch (err) {
        if (active) {
          console.error("Erro no useDashboard hook:", err);
          setError("Erro ao carregar dados do dashboard.");
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
  }, [filtros]);

  return {
    metricas,
    pipelineData,
    timeSeriesData,
    bottleneckData,
    houseTransitionData,
    estoqueData,
    handoffData,
    coberturaData,
    qualidadeData,
    loading,
    error
  };
}
