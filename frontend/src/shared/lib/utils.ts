import { differenceInDays, format, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { DIAS_ATRASO_SIGNIFICATIVO } from '../constants'
import type { StatusProposicao } from '../types'

export function formatarData(data: string): string {
  return format(parseISO(data), "dd 'de' MMMM 'de' yyyy", { locale: ptBR })
}

export function formatarDataCurta(data: string): string {
  return format(parseISO(data), 'dd/MM/yyyy', { locale: ptBR })
}

export function calcularDiasEntreatas(dataInicio: string, dataFim?: string): number {
  const fim = dataFim ? parseISO(dataFim) : new Date()
  return differenceInDays(fim, parseISO(dataInicio))
}

export function formatarTempo(dias: number): string {
  if (dias < 30) return `${dias} dias`
  if (dias < 365) return `${Math.floor(dias / 30)} meses`
  const anos = Math.floor(dias / 365)
  const meses = Math.floor((dias % 365) / 30)
  if (meses === 0) return `${anos} ${anos === 1 ? 'ano' : 'anos'}`
  return `${anos} ${anos === 1 ? 'ano' : 'anos'} e ${meses} ${meses === 1 ? 'mês' : 'meses'}`
}

export function corStatus(status: StatusProposicao): string {
  const mapa: Record<StatusProposicao, string> = {
    'Em tramitação': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    'Aprovada': 'bg-volt-400/20 text-volt-300 border-volt-400/30',
    'Rejeitada': 'bg-rose-500/20 text-rose-300 border-rose-500/30',
    'Arquivada': 'bg-ink-400/20 text-ink-300 border-ink-400/30',
    'Vetada': 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    'Sancionada': 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    'Aguardando votação': 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    'Em análise': 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  }
  return mapa[status] ?? 'bg-ink-400/20 text-ink-300 border-ink-400/30'
}

export function corTipo(tipo: string): string {
  const mapa: Record<string, string> = {
    PL: 'bg-indigo-500/20 text-indigo-300',
    PEC: 'bg-amber-500/20 text-amber-300',
    PDL: 'bg-cyan-500/20 text-cyan-300',
    MP: 'bg-rose-500/20 text-rose-300',
    PLP: 'bg-violet-500/20 text-violet-300',
  }
  return mapa[tipo] ?? 'bg-ink-400/20 text-ink-300'
}

export function paginar<T>(items: T[], pagina: number, itensPorPagina: number): T[] {
  const inicio = (pagina - 1) * itensPorPagina
  return items.slice(inicio, inicio + itensPorPagina)
}

