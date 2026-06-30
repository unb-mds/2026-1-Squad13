export type TipoProposicao = 'PL' | 'PEC' | 'PDL' | 'MP' | 'PLP'

export type StatusProposicao =
  | 'Em Tramitação'
  | 'Em Pauta'
  | 'Aprovada'
  | 'Sancionada'
  | 'Vetada'
  | 'Arquivada'

export interface BreakdownFase {
  fase: string
  dias: number
}

export interface Proposicao {
  id: string
  tipo: TipoProposicao
  numero: string
  ano: number
  ementa: string
  ementaResumida: string
  autor: string
  orgaoOrigem: string
  status: StatusProposicao
  statusOriginal?: string
  orgaoAtual: string
  dataApresentacao: string
  dataUltimaMovimentacao: string
  dataEncerramento?: string
  linkOficial?: string
  codigoNormalizado?: string
  tempoTotalDias: number
  temAtraso: boolean
  atrasoCritico: boolean
  temPrevisaoIA: boolean
  previsaoAprovacaoDias?: number
  coberturaDados: number
  confiabilidade: 'alta' | 'media' | 'baixa'
  tempoPorFase?: BreakdownFase[]
  tags: string[]
  transitSteps?: {
    casa: string
    tipoPasso: string
    dataEntrada: string
    dataSaida?: string
    duracaoDias: number
  }[]
}

export interface MovimentacaoTramitacao {
  id: string
  proposicaoId: string
  data: string
  orgao: string
  descricao: string
  responsavel?: string
  diasNaEtapa: number
  temAtraso: boolean
}

export interface TrendInfo {
  value: string
  isPositive: boolean
}

export interface MetricasDashboard {
  tempoMedioTramitacao: number
  totalProposicoes: number
  totalTramitacoes: number
  proposicoesComAtraso: number
  comissaoMaiorTempo: string
  comissaoMaiorTempoMedia: number
  totalAprovadas: number
  totalEmTramitacao: number
  totalRejeitadas: number
  totalProposicoesTrend?: TrendInfo
  totalEmTramitacaoTrend?: TrendInfo
  proposicoesComAtrasoTrend?: TrendInfo;
  tempoMedioTramitacaoTrend?: TrendInfo;
}

export interface DadosGraficoTipo {
  tipo: string
  tempoMedio: number
  quantidade: number
}

export interface DadosGraficoComissao {
  comissao: string
  tempoMedio: number
  quantidade: number
}

export interface DadosGraficoStatus {
  status: string
  quantidade: number
  percentual: number
}

export interface GargaloInstitucional {
  orgao: string
  tempoMedioMeses: number
  quantidadeProposicoes: number
  taxaAtraso: number
}

export interface ComparacaoTema {
  tema: string
  tempoMedioDias: number
  taxaAprovacao: number
  velocidade: 'rapido' | 'medio' | 'lento'
}

export interface TempoPorFase {
  fase: string
  codigoFase: string
  ordemLogica: number
  tempoMedioDias: number
  quantidadeProposicoes: number
}

export interface FiltrosProposicao {
  busca: string
  orgaoOrigem: string
  tipo: string
  status: string
  dataInicio: string
  dataFim: string
  rito?: string
}

export interface PaginacaoState {
  pagina: number
  itensPorPagina: number
  total: number
}

export interface EstoqueFaseItem {
  codigo: string
  nome: string
  natureza: string
  permiteEstoqueAtual: boolean
  total: number
}

export interface DashboardEstoqueResponse {
  ativo: EstoqueFaseItem[]
  passivo: EstoqueFaseItem[]
}

export interface DashboardHandoffResponse {
  totalEmTransito: number
  medianaDiasTransito: number
}

export interface CoberturaMetricaResponse {
  ano: number
  tipoProposicao: string
  totalLocal: number
  totalApiOficial: number
  percentualCobertura: number
  dataAtualizacao: string | null
}

export interface DashboardQualidadeResponse {
  completudePorcentagem: number
  totalProposicoes: number
  camposAnalisados: number
}
