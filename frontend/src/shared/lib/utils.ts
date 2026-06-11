import { differenceInDays, format, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import type { StatusProposicao } from '../types'

export function formatarData(data?: string): string {
  if (!data) return 'Data não informada'
  try {
    const parsed = parseISO(data)
    if (isNaN(parsed.getTime())) return 'Data inválida'
    return format(parsed, "dd 'de' MMMM 'de' yyyy", { locale: ptBR })
  } catch {
    return 'Erro na data'
  }
}

export function formatarDataCurta(data?: string): string {
  if (!data) return 'N/A'
  try {
    const parsed = parseISO(data)
    if (isNaN(parsed.getTime())) return 'Inválida'
    return format(parsed, 'dd/MM/yyyy', { locale: ptBR })
  } catch {
    return 'N/A'
  }
}

export function calcularDiasEntreatas(dataInicio: string, dataFim?: string): number {
  try {
    const inicio = parseISO(dataInicio)
    if (isNaN(inicio.getTime())) return 0
    const fim = dataFim ? parseISO(dataFim) : new Date()
    if (isNaN(fim.getTime())) return 0
    return differenceInDays(fim, inicio)
  } catch {
    return 0
  }
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
    'Em Tramitação': 'bg-info/10 text-info border-info/20',
    'Em Pauta': 'bg-info/10 text-info border-info/20',
    'Aprovada': 'bg-primary/10 text-primary border-primary/20',
    'Sancionada': 'bg-primary/10 text-primary border-primary/20',
    'Vetada': 'bg-destructive/10 text-destructive border-destructive/20',
    'Arquivada': 'bg-muted text-muted-foreground border-border',
  }
  return mapa[status] ?? 'bg-muted text-muted-foreground border-border'
}

export function corTipo(tipo: string): string {
  const mapa: Record<string, string> = {
    PL: 'bg-info/10 text-info',
    PEC: 'bg-warning/10 text-warning',
    PDL: 'bg-accent text-accent-foreground',
    MP: 'bg-destructive/10 text-destructive',
    PLP: 'bg-primary/10 text-primary',
  }
  return mapa[tipo] ?? 'bg-muted text-muted-foreground'
}

export function paginar<T>(items: T[], pagina: number, itensPorPagina: number): T[] {
  const inicio = (pagina - 1) * itensPorPagina
  return items.slice(inicio, inicio + itensPorPagina)
}

