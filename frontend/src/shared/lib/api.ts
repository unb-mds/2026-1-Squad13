import { PROPOSICOES_MOCK, getMovimentacoes } from '../lib/mock-data'
import { filtrarProposicoes, paginar } from '../lib/utils'
import type {
  Proposicao,
  MovimentacaoTramitacao,
  MetricasDashboard,
  DadosGraficoTipo,
  DadosGraficoComissao,
  DadosGraficoStatus,
  GargaloInstitucional,
  ComparacaoTema,
  FiltrosProposicao,
} from '../types'

const delay = (ms: number) => new Promise((res) => setTimeout(res, ms))

// --- Auth ---
export async function loginApi(email: string, senha: string): Promise<{ token: string; user: { id: string; nome: string; email: string; perfil: 'analista' } }> {
  await delay(800)
  if (email === 'demo@lextrack.gov.br' && senha === 'demo123') {
    return {
      token: 'fake-jwt-token-' + Date.now(),
      user: { id: '1', nome: 'Ana Paula Legislativa', email, perfil: 'analista' },
    }
  }
  if (email && senha.length >= 6) {
    return {
      token: 'fake-jwt-token-' + Date.now(),
      user: { id: '2', nome: email.split('@')[0], email, perfil: 'analista' },
    }
  }
  throw new Error('Credenciais inválidas. Verifique seu e-mail e senha.')
}

export async function cadastroApi(nome: string, email: string, _senha: string): Promise<{ token: string; user: { id: string; nome: string; email: string; perfil: 'analista' } }> {
  await delay(1000)
  return {
    token: 'fake-jwt-token-' + Date.now(),
    user: { id: '3', nome, email, perfil: 'analista' },
  }
}

export async function recuperarSenhaApi(_email: string): Promise<void> {
  await delay(1200)
}

// --- Proposições ---
export async function listarProposicoes(
  filtros: FiltrosProposicao,
  _pagina: number,
  _itensPorPagina: number
): Promise<{ items: Proposicao[]; total: number }> {
  const params = new URLSearchParams()

  if (filtros.tipo) params.append('tipo', filtros.tipo)
  if (filtros.status) params.append('status_tramitacao', filtros.status)
  
  // Tentando extrair ano da busca ou das datas para o backend atual
  if (filtros.dataInicio) {
    const ano = new Date(filtros.dataInicio).getFullYear()
    if (!isNaN(ano)) params.append('ano', ano.toString())
  }

  // Se a busca for um número, enviamos como número para o backend
  if (/^\d+$/.test(filtros.busca)) {
    params.append('numero', filtros.busca)
  } else if (filtros.busca) {
    params.append('autor', filtros.busca)
  }

  try {
    const response = await fetch(`http://localhost:8000/proposicoes?${params.toString()}`)
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Erro ao buscar proposições')
    }

    const data = await response.json()
    
    // Mapeamento para adaptar o que o backend retorna ao que o frontend espera
    const items = data.items.map((item: any) => ({
      id: String(item.id),
      tipo: item.tipo,
      numero: String(item.numero),
      ano: item.ano,
      ementa: item.ementa,
      ementaResumida: item.ementa.substring(0, 100) + '...',
      autor: item.autor,
      orgaoOrigem: item.tipo === 'PEC' ? 'Senado Federal' : 'Câmara dos Deputados', // Lógica simples baseada no tipo
      status: item.statusTramitacao,
      orgaoAtual: item.orgaoAtual,
      dataApresentacao: item.dataApresentacao,
      dataUltimaMovimentacao: item.dataUltimaMovimentacao,
      linkOficial: item.linkOficial,
      tempoTotalDias: 0, // Poderia ser calculado aqui se quisermos
      temAtraso: false,
      temPrevisaoIA: false,
      tags: item.tags,
    }))

    return { items, total: data.total }
  } catch (error) {
    console.error('Erro na API:', error)
    throw error
  }
}

export async function obterProposicao(id: string): Promise<Proposicao | null> {
  await delay(400)
  return PROPOSICOES_MOCK.find((p) => p.id === id) ?? null
}

export async function obterMovimentacoes(proposicaoId: string): Promise<MovimentacaoTramitacao[]> {
  await delay(300)
  const proposicao = PROPOSICOES_MOCK.find((p) => p.id === proposicaoId)
  if (!proposicao) return []
  return getMovimentacoes(proposicaoId, proposicao)
}

// --- Dashboard ---
export async function obterMetricas(): Promise<MetricasDashboard> {
  await delay(600)
  return {
    tempoMedioTramitacao: 412,
    totalProposicoes: PROPOSICOES_MOCK.length,
    proposicoesComAtraso: PROPOSICOES_MOCK.filter((p) => p.temAtraso).length,
    comissaoMaiorTempo: 'CCJ',
    comissaoMaiorTempoMedia: 680,
    totalAprovadas: PROPOSICOES_MOCK.filter((p) => p.status === 'Aprovada' || p.status === 'Sancionada').length,
    totalEmTramitacao: PROPOSICOES_MOCK.filter((p) => p.status === 'Em tramitação' || p.status === 'Em análise' || p.status === 'Aguardando votação').length,
    totalRejeitadas: PROPOSICOES_MOCK.filter((p) => p.status === 'Rejeitada' || p.status === 'Arquivada').length,
  }
}

export async function obterDadosTipo(): Promise<DadosGraficoTipo[]> {
  await delay(400)
  return [
    { tipo: 'PL', tempoMedio: 380, quantidade: 7 },
    { tipo: 'PEC', tempoMedio: 477, quantidade: 3 },
    { tipo: 'MP', tempoMedio: 180, quantidade: 1 },
    { tipo: 'PLP', tempoMedio: 43, quantidade: 1 },
  ]
}

export async function obterDadosComissao(): Promise<DadosGraficoComissao[]> {
  await delay(400)
  return [
    { comissao: 'CCJ', tempoMedio: 680, quantidade: 8 },
    { comissao: 'CFT', tempoMedio: 510, quantidade: 5 },
    { comissao: 'CAS', tempoMedio: 390, quantidade: 4 },
    { comissao: 'CMADS', tempoMedio: 340, quantidade: 3 },
    { comissao: 'CTASP', tempoMedio: 295, quantidade: 4 },
    { comissao: 'CDH', tempoMedio: 260, quantidade: 2 },
  ]
}

export async function obterDadosStatus(): Promise<DadosGraficoStatus[]> {
  await delay(300)
  const total = PROPOSICOES_MOCK.length
  const contagem: Record<string, number> = {}
  PROPOSICOES_MOCK.forEach((p) => {
    contagem[p.status] = (contagem[p.status] ?? 0) + 1
  })
  return Object.entries(contagem).map(([status, quantidade]) => ({
    status,
    quantidade,
    percentual: Math.round((quantidade / total) * 100),
  }))
}

// --- Relatórios ---
export async function obterGargalos(): Promise<GargaloInstitucional[]> {
  await delay(500)
  return [
    { orgao: 'CCJ', tempoMedioMeses: 22, quantidadeProposicoes: 8, taxaAtraso: 62 },
    { orgao: 'CFT', tempoMedioMeses: 17, quantidadeProposicoes: 5, taxaAtraso: 40 },
    { orgao: 'CAS', tempoMedioMeses: 13, quantidadeProposicoes: 4, taxaAtraso: 25 },
    { orgao: 'CMADS', tempoMedioMeses: 11, quantidadeProposicoes: 3, taxaAtraso: 33 },
    { orgao: 'Plenário Câmara', tempoMedioMeses: 18, quantidadeProposicoes: 6, taxaAtraso: 50 },
  ]
}

export async function obterComparacaoTemas(): Promise<ComparacaoTema[]> {
  await delay(400)
  return [
    { tema: 'Tributário', tempoMedioDias: 215, taxaAprovacao: 78, velocidade: 'rapido' },
    { tema: 'Educação', tempoMedioDias: 380, taxaAprovacao: 55, velocidade: 'medio' },
    { tema: 'Tecnologia & IA', tempoMedioDias: 310, taxaAprovacao: 42, velocidade: 'medio' },
    { tema: 'Reforma Administrativa', tempoMedioDias: 920, taxaAprovacao: 18, velocidade: 'lento' },
    { tema: 'Previdência', tempoMedioDias: 266, taxaAprovacao: 70, velocidade: 'rapido' },
    { tema: 'Internet & Mídia', tempoMedioDias: 1322, taxaAprovacao: 12, velocidade: 'lento' },
    { tema: 'Trabalho & Emprego', tempoMedioDias: 538, taxaAprovacao: 60, velocidade: 'medio' },
    { tema: 'Meio Ambiente', tempoMedioDias: 726, taxaAprovacao: 30, velocidade: 'lento' },
  ]
}
