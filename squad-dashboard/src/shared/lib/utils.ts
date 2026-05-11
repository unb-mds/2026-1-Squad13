import type { TaskPriority, TaskStatus, TaskLabel } from '@/entities/task'
import type { FeatureStatus } from '@/entities/feature'

export function cn(...classes: (string | undefined | false | null)[]): string {
  return classes.filter(Boolean).join(' ')
}

export const PRIORITY_CONFIG: Record<TaskPriority, { label: string; color: string; dot: string }> = {
  critical: { label: 'Crítica', color: 'text-red-400', dot: 'bg-red-400' },
  high: { label: 'Alta', color: 'text-orange-400', dot: 'bg-orange-400' },
  medium: { label: 'Média', color: 'text-yellow-400', dot: 'bg-yellow-400' },
  low: { label: 'Baixa', color: 'text-slate-400', dot: 'bg-slate-400' },
}

export const STATUS_CONFIG: Record<TaskStatus, { label: string; color: string }> = {
  backlog: { label: 'Backlog', color: 'text-slate-400' },
  todo: { label: 'A Fazer', color: 'text-blue-400' },
  in_progress: { label: 'Em Progresso', color: 'text-yellow-400' },
  review: { label: 'Em Review', color: 'text-purple-400' },
  done: { label: 'Concluída', color: 'text-green-400' },
}

export const LABEL_CONFIG: Record<TaskLabel, { label: string; bg: string; text: string }> = {
  feature: { label: 'feature', bg: 'bg-blue-500/15', text: 'text-blue-400' },
  bug: { label: 'bug', bg: 'bg-red-500/15', text: 'text-red-400' },
  chore: { label: 'chore', bg: 'bg-slate-500/15', text: 'text-slate-400' },
  docs: { label: 'docs', bg: 'bg-yellow-500/15', text: 'text-yellow-400' },
  test: { label: 'test', bg: 'bg-purple-500/15', text: 'text-purple-400' },
}

export const FEATURE_STATUS_CONFIG: Record<FeatureStatus, { label: string; bg: string; text: string }> = {
  planned: { label: 'Planejada', bg: 'bg-slate-500/15', text: 'text-slate-400' },
  in_progress: { label: 'Em Progresso', bg: 'bg-blue-500/15', text: 'text-blue-400' },
  review: { label: 'Em Review', bg: 'bg-purple-500/15', text: 'text-purple-400' },
  done: { label: 'Concluída', bg: 'bg-green-500/15', text: 'text-green-400' },
  blocked: { label: 'Bloqueada', bg: 'bg-red-500/15', text: 'text-red-400' },
}

export function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })
}
