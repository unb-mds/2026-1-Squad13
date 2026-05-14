/**
 * Utilitários para métricas do Squad Dashboard.
 */

export interface BurnupPoint {
  date: string
  label: string
  plannedScope: number
  deliveredR1: number
  deliveredTotal: number
  idealR1: number
  idealTotal: number
  isFuture: boolean
}

// Lógica de cálculo movida para o backend (generate-github-data.mjs) 
// para garantir consistência e auditabilidade.
