import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { DashboardPage } from '../dashboard-page'

describe('DashboardPage', () => {
  it('deve renderizar o titulo corretamente', () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText(/Squad 13/)).toBeInTheDocument()
  })

  it('deve exibir os cards de KPI principais', () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )

    expect(screen.getByText('Tasks Concluídas')).toBeInTheDocument()
    expect(screen.getByText('PRs Mergeados')).toBeInTheDocument()
    expect(screen.getByText('Progresso Geral')).toBeInTheDocument()
  })
})
