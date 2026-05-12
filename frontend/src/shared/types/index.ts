export type TipoProposicao = 'PL' | 'PEC' | 'PDL' | 'MP' | 'PLP'

export type StatusProposicao =
  | 'Em tramitação'
  | 'Aprovada'
  | 'Rejeitada'
  | 'Arquivada'
  | 'Vetada'
  | 'Sancionada'
  | 'Aguardando votação'
  | 'Em análise'

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
  orgaoAtual: string
  dataApresentacao: string
  dataUltimaMovimentacao: string
  dataEncerramento?: string
  linkOficial?: string
  tempoTotalDias: number
  temAtraso: boolean
  atrasoCritico: boolean
  temPrevisaoIA: boolean
  previsaoAprovacaoDias?: number
  tags: string[]
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

export interface MetricasDashboard {
  tempoMedioTramitacao: number
  totalProposicoes: number
  proposicoesComAtraso: number
  comissaoMaiorTempo: string
  comissaoMaiorTempoMedia: number
  totalAprovadas: number
  totalEmTramitacao: number
  totalRejeitadas: number
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

export interface User {
  id: string
  nome: string
  email: string
  perfil: 'analista' | 'gestor' | 'publico'
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  expiresAt: number | null
}

export interface FiltrosProposicao {
  busca: string
  orgaoOrigem: string
  tipo: string
  status: string
  dataInicio: string
  dataFim: string
}

export interface PaginacaoState {
  pagina: number
  itensPorPagina: number
  total: number
}
