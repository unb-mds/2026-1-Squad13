import type { Proposicao, FiltrosProposicao } from '@/shared/types'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

interface ProposicoesApiResponse {
  items: Proposicao[]
  total: number
  pagina: number
  totalPaginas: number
}

export async function buscarProposicoes(
  filtros: FiltrosProposicao,
  pagina: number,
  itensPorPagina: number,
): Promise<{ items: Proposicao[]; total: number }> {
  const params = new URLSearchParams()

  if (filtros.busca) params.set('busca', filtros.busca)
  if (filtros.tipo) params.set('tipo', filtros.tipo)
  if (filtros.status) params.set('status', filtros.status)
  if (filtros.orgaoOrigem) params.set('orgaoOrigem', filtros.orgaoOrigem)
  if (filtros.dataInicio) params.set('dataInicio', filtros.dataInicio)
  if (filtros.dataFim) params.set('dataFim', filtros.dataFim)
  params.set('pagina', String(pagina))
  params.set('itensPorPagina', String(itensPorPagina))

  const response = await fetch(`${API_BASE}/proposicoes?${params.toString()}`)

  if (!response.ok) {
    throw new Error(`Erro ao buscar proposições (${response.status})`)
  }

  const data: ProposicoesApiResponse = await response.json()
  return { items: data.items, total: data.total }
}
