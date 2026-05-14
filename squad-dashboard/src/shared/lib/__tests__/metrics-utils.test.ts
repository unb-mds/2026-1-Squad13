import { describe, it, expect } from 'vitest'
import { calculateBurndown } from '../metrics-utils'

describe('calculateBurndown', () => {
  const today = new Date('2026-05-13T12:00:00Z')
  
  it('deve calcular corretamente o burndown com escopo fixo', () => {
    const issues = [
      { createdAt: '2026-04-20T10:00:00Z', closedAt: '2026-05-10T10:00:00Z' },
      { createdAt: '2026-04-25T10:00:00Z', closedAt: null },
      { createdAt: '2026-04-28T10:00:00Z', closedAt: '2026-05-12T10:00:00Z' },
    ]
    
    const daysToShow = 10
    const result = calculateBurndown(issues, daysToShow, today)
    
    expect(result).toHaveLength(daysToShow + 1)
    
    // Na data de início (10 dias antes de 13/Maio = 03/Maio)
    // Todas as 3 issues existiam e estavam abertas
    expect(result[0].remaining).toBe(3)
    expect(result[0].scope).toBe(3)
    
    // No dia 10/Maio uma foi fechada
    const day10 = result.find(r => r.date === '2026-05-10')
    expect(day10?.remaining).toBe(2)
    expect(day10?.completedItems).toBe(1)
  })

  it('deve identificar aumento de escopo corretamente', () => {
    const issues = [
      { createdAt: '2026-04-20T10:00:00Z', closedAt: null }, // Escopo inicial
      { createdAt: '2026-05-10T10:00:00Z', closedAt: null }, // Adicionado durante a sprint
    ]
    
    const daysToShow = 10
    const result = calculateBurndown(issues, daysToShow, today)
    
    const dayStart = result[0]
    const dayEnd = result[result.length - 1]
    
    expect(dayStart.scope).toBe(1)
    expect(dayEnd.scope).toBe(2)
    expect(dayEnd.addedItems).toBe(0) // 13/Maio não adicionou nada
    
    const day10 = result.find(r => r.date === '2026-05-10')
    expect(day10?.addedItems).toBe(1)
  })
})
