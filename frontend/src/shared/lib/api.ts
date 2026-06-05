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
  TempoPorFase,
} from '../types'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

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

export async function obterMovimentacoes(proposicaoId: string, modo: 'completo' | 'relevante' = 'completo'): Promise<MovimentacaoTramitacao[]> {
  try {
    const response = await fetch(`${API_BASE}/proposicoes/${proposicaoId}/movimentacoes?modo=${modo}`)

    if (!response.ok) {
      return []
    }

    const rawData = await response.json()
    if (!Array.isArray(rawData)) return []

    // Normalização das propriedades do Backend para a interface do Frontend
    return (rawData as Array<{
      proposicaoId: string;
      dataEvento: string;
      sequencia: number;
      siglaOrgao: string;
      descricaoOriginal: string;
      diasNaEtapa: number;
      temAtraso: boolean;
    }>).map((d) => ({
      id: String(d.sequencia || Math.random()),
      proposicaoId: d.proposicaoId || '',
      data: d.dataEvento || '',
      orgao: d.siglaOrgao || 'N/A',
      descricao: d.descricaoOriginal || 'Movimentação registrada',
      responsavel: undefined,
      diasNaEtapa: d.diasNaEtapa || 0,
      temAtraso: d.temAtraso || false,
    }))
  } catch {
    return []
  }
}

export async function obterMovimentacoesFases(proposicaoId: string): Promise<unknown[]> {
  try {
    const response = await fetch(`${API_BASE}/proposicoes/${proposicaoId}/movimentacoes?modo=resumido`)
    if (!response.ok) return []
    return await response.json()
  } catch {
    return []
  }
}

export async function obterMovimentacoesEventos(proposicaoId: string, modo: 'completo' | 'relevante' = 'relevante'): Promise<unknown[]> {
  try {
    const response = await fetch(`${API_BASE}/proposicoes/${proposicaoId}/movimentacoes?modo=${modo}`)
    if (!response.ok) return []
    return await response.json()
  } catch {
    return []
  }
}


// --- Dashboard ---
function _filtrosParaParams(filtros?: Partial<FiltrosProposicao>): string {
  if (!filtros) return ''
  const params = new URLSearchParams()
  if (filtros.busca) params.append('busca', filtros.busca)
  if (filtros.tipo) params.append('tipo', filtros.tipo)
  if (filtros.status) params.append('status', filtros.status)
  if (filtros.orgaoOrigem) params.append('orgaoOrigem', filtros.orgaoOrigem)
  if (filtros.dataInicio) params.append('dataInicio', filtros.dataInicio)
  if (filtros.dataFim) params.append('dataFim', filtros.dataFim)
  const qs = params.toString()
  return qs ? `?${qs}` : ''
}

export async function obterMetricas(filtros?: Partial<FiltrosProposicao>): Promise<MetricasDashboard> {
  const response = await fetch(`${API_BASE}/dashboard/metricas${_filtrosParaParams(filtros)}`)
  if (!response.ok) throw new Error('Falha ao buscar métricas da API')
  return await response.json()
}

export async function obterDadosTipo(filtros?: Partial<FiltrosProposicao>): Promise<DadosGraficoTipo[]> {
  const response = await fetch(`${API_BASE}/dashboard/grafico-tipo${_filtrosParaParams(filtros)}`)
  if (!response.ok) throw new Error('Falha ao buscar dados por tipo')
  return await response.json()
}

export async function obterDadosComissao(filtros?: Partial<FiltrosProposicao>): Promise<DadosGraficoComissao[]> {
  const response = await fetch(`${API_BASE}/dashboard/grafico-comissao${_filtrosParaParams(filtros)}`)
  if (!response.ok) throw new Error('Falha ao buscar dados por comissão')
  return await response.json()
}

export async function obterDadosStatus(filtros?: Partial<FiltrosProposicao>): Promise<DadosGraficoStatus[]> {
  const response = await fetch(`${API_BASE}/dashboard/grafico-status${_filtrosParaParams(filtros)}`)
  if (!response.ok) throw new Error('Falha ao buscar dados por status')
  return await response.json()
}

// --- Relatórios ---
export async function obterGargalos(filtros?: Partial<FiltrosProposicao>): Promise<GargaloInstitucional[]> {
  const response = await fetch(`${API_BASE}/dashboard/gargalos${_filtrosParaParams(filtros)}`)
  if (!response.ok) throw new Error('Falha ao buscar gargalos da API')
  return await response.json()
}

export async function obterComparacaoTemas(filtros?: Partial<FiltrosProposicao>): Promise<ComparacaoTema[]> {
  const response = await fetch(`${API_BASE}/dashboard/comparacao-temas${_filtrosParaParams(filtros)}`)
  if (!response.ok) throw new Error('Falha ao buscar comparação de temas')
  return await response.json()
}

export async function obterTempoPorFase(filtros?: Partial<FiltrosProposicao>): Promise<TempoPorFase[]> {
  const response = await fetch(`${API_BASE}/dashboard/tempo-por-fase${_filtrosParaParams(filtros)}`)
  if (!response.ok) throw new Error('Falha ao buscar tempo por fase')
  return await response.json()
}

export async function obterEvolucaoTemporal(filtros?: Partial<FiltrosProposicao>): Promise<unknown[]> {
  const response = await fetch(`${API_BASE}/dashboard/evolucao-temporal${_filtrosParaParams(filtros)}`)
  if (!response.ok) throw new Error('Falha ao buscar evolução temporal')
  return await response.json()
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function obterTransicoesCasas(filtros?: Partial<FiltrosProposicao>): Promise<any> {
  const response = await fetch(`${API_BASE}/dashboard/transicoes-casas${_filtrosParaParams(filtros)}`)
  if (!response.ok) throw new Error('Falha ao buscar transições de casas')
  return await response.json()
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function obterConfiabilidade(proposicaoId: string): Promise<any> {
  const response = await fetch(`${API_BASE}/proposicoes/${proposicaoId}/confiabilidade`)
  if (!response.ok) throw new Error('Falha ao buscar confiabilidade da proposição')
  return await response.json()
}

