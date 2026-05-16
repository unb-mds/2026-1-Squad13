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

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const delay = (ms: number) => new Promise((res) => setTimeout(res, ms))

// --- Auth ---
export async function loginApi(email: string, senha: string): Promise<{ token: string; user: { id: string; nome: string; email: string; perfil: 'analista' } }> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password: senha }),
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail || 'Credenciais inválidas. Verifique seu e-mail e senha.')
  }

  const data = await response.json()
  
  return {
    token: data.access_token,
    user: {
      id: String(data.user.id),
      nome: data.user.nome,
      email: data.user.email,
      perfil: data.user.perfil,
    },
  }
}

export async function cadastroApi(nome: string, email: string, senha: string): Promise<{ token: string; user: { id: string; nome: string; email: string; perfil: 'analista' } }> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome, email, password: senha }),
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail || 'Erro ao realizar cadastro.')
  }

  // Após o cadastro, fazemos o login automaticamente para obter o token
  return loginApi(email, senha)
}

export async function recuperarSenhaApi(_email: string): Promise<void> {
  await delay(1200)
}

// --- Proposições ---
export async function listarProposicoes(
  filtros: FiltrosProposicao,
  pagina: number,
  itensPorPagina: number
): Promise<{ items: Proposicao[]; total: number }> {
  const params = new URLSearchParams()

  if (filtros.busca) params.append('busca', filtros.busca)
  if (filtros.tipo) params.append('tipo', filtros.tipo)
  if (filtros.status) params.append('status', filtros.status)
  if (filtros.orgaoOrigem) params.append('orgaoOrigem', filtros.orgaoOrigem)
  if (filtros.dataInicio) params.append('dataInicio', filtros.dataInicio)
  if (filtros.dataFim) params.append('dataFim', filtros.dataFim)
  params.append('pagina', String(pagina))
  params.append('itens_por_pagina', String(itensPorPagina))

  const response = await fetch(`${API_BASE}/proposicoes?${params.toString()}`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Falha ao buscar proposições')
  }

  const data = await response.json()
  return { items: data.items, total: data.total }
}

export async function obterProposicao(id: string): Promise<Proposicao | null> {
  const response = await fetch(`${API_BASE}/proposicoes/${id}`)

  if (!response.ok) {
    if (response.status === 404) return null
    throw new Error('Falha ao buscar detalhe da proposição')
  }

  return await response.json()
}

export async function obterMovimentacoes(proposicaoId: string): Promise<MovimentacaoTramitacao[]> {
  const response = await fetch(`${API_BASE}/proposicoes/${proposicaoId}/movimentacoes`)

  if (!response.ok) {
    throw new Error('Falha ao buscar movimentações')
  }

  const rawData = await response.json()
  // Normalização das propriedades do Backend para a interface do Frontend
  return (rawData as Array<{
    sequencia?: number;
    proposicaoId: string;
    dataHora?: string;
    siglaOrgao?: string;
    descricaoTramitacao?: string;
  }>).map((d, index) => ({
    id: d.sequencia ? String(d.sequencia) : String(index),
    proposicaoId: d.proposicaoId,
    data: d.dataHora || new Date().toISOString(),
    orgao: d.siglaOrgao || 'N/A',
    descricao: d.descricaoTramitacao || 'Tramitação registrada',
    responsavel: undefined,
    diasNaEtapa: 0,
    temAtraso: false,
  }))
}

// --- Dashboard ---
export async function obterMetricas(): Promise<MetricasDashboard> {
  const response = await fetch(`${API_BASE}/dashboard/metricas`)
  if (!response.ok) throw new Error('Falha ao buscar métricas da API')
  return await response.json()
}

export async function obterDadosTipo(): Promise<DadosGraficoTipo[]> {
  const response = await fetch(`${API_BASE}/dashboard/grafico-tipo`)
  if (!response.ok) throw new Error('Falha ao buscar dados por tipo')
  return await response.json()
}

export async function obterDadosComissao(): Promise<DadosGraficoComissao[]> {
  const response = await fetch(`${API_BASE}/dashboard/grafico-comissao`)
  if (!response.ok) throw new Error('Falha ao buscar dados por comissão')
  return await response.json()
}

export async function obterDadosStatus(): Promise<DadosGraficoStatus[]> {
  const response = await fetch(`${API_BASE}/dashboard/grafico-status`)
  if (!response.ok) throw new Error('Falha ao buscar dados por status')
  return await response.json()
}

// --- Relatórios ---
export async function obterGargalos(): Promise<GargaloInstitucional[]> {
  const response = await fetch(`${API_BASE}/dashboard/gargalos`)
  if (!response.ok) throw new Error('Falha ao buscar gargalos da API')
  return await response.json()
}

export async function obterComparacaoTemas(): Promise<ComparacaoTema[]> {
  const response = await fetch(`${API_BASE}/dashboard/comparacao-temas`)
  if (!response.ok) throw new Error('Falha ao buscar comparação de temas')
  return await response.json()
}

