/**
 * Lógica central para cálculo de Burndown semântico.
 * Separada para facilitar testes unitários e reuso.
 */

export interface IssueHistory {
  createdAt: string // ISO date
  closedAt: string | null // ISO date or null
}

export interface BurndownPoint {
  date: string
  label: string
  remaining: number
  ideal: number
  scope: number
  addedItems: number
  completedItems: number
}

export function calculateBurndown(
  issues: IssueHistory[],
  daysToShow: number,
  today: Date = new Date()
): BurndownPoint[] {
  const startDate = new Date(today)
  startDate.setDate(today.getDate() - daysToShow)
  
  // Escopo inicial: issues que existiam na data de início
  const initialScopeCount = issues.filter(i => {
    const created = new Date(i.createdAt)
    return created <= startDate
  }).length

  const burndownData: BurndownPoint[] = []
  
  for (let i = 0; i <= daysToShow; i++) {
    const targetDate = new Date(startDate)
    targetDate.setDate(startDate.getDate() + i)
    const dateStr = targetDate.toISOString().slice(0, 10)
    
    // Issues abertas no final deste dia
    const openOnDate = issues.filter(i => {
      const created = i.createdAt.slice(0, 10)
      const closed = i.closedAt ? i.closedAt.slice(0, 10) : '9999-12-31'
      return created <= dateStr && closed > dateStr
    }).length

    // Itens adicionados NESTE dia (escopo novo)
    const addedToday = issues.filter(i => 
      i.createdAt.slice(0, 10) === dateStr && new Date(i.createdAt) > startDate
    ).length
    
    // Itens concluídos NESTE dia
    const completedToday = issues.filter(i => 
      i.closedAt && i.closedAt.slice(0, 10) === dateStr
    ).length

    // Escopo total acumulado até este dia
    const totalScopeOnDate = issues.filter(i => i.createdAt.slice(0, 10) <= dateStr).length

    burndownData.push({
      date: dateStr,
      label: targetDate.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' }),
      remaining: openOnDate,
      ideal: Math.max(0, Math.round(initialScopeCount - (initialScopeCount / daysToShow) * i)),
      scope: totalScopeOnDate,
      addedItems: addedToday,
      completedItems: completedToday
    })
  }

  return burndownData
}
