import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { DashboardPage } from '../dashboard-page'
import * as githubService from '@/shared/api/github-data-service'

// Mock do hook de dados
vi.mock('@/shared/api/github-data-service', () => ({
  useGithubData: vi.fn()
}))

describe('DashboardPage - Simplificação Pragmática', () => {
  it('deve exibir skeletons enquanto os dados estão carregando', () => {
    vi.mocked(githubService.useGithubData).mockReturnValue({
      data: null,
      loading: true,
      error: false
    })

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )
    
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('deve exibir apenas os 4 KPIs essenciais quando os dados carregam', () => {
    vi.mocked(githubService.useGithubData).mockReturnValue({
      data: {
        generatedAt: new Date().toISOString(),
        issues: { open: 5, closed: 5 },
        milestones: [],
        features: [],
        burndownData: [],
        commitsByDay: []
      } as any,
      loading: false,
      error: false
    })

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )

    expect(screen.getByText('Entregue')).toBeInTheDocument()
    expect(screen.getByText('Em Aberto')).toBeInTheDocument()
    expect(screen.getByText('Progresso MVP')).toBeInTheDocument()
    expect(screen.getByText('Próxima Entrega')).toBeInTheDocument()

    // Verifica que KPIs antigos foram removidos
    expect(screen.queryByText('Tasks Concluídas')).not.toBeInTheDocument()
    expect(screen.queryByText('PRs Mergeados')).not.toBeInTheDocument()
    expect(screen.queryByText('Bugs Abertos')).not.toBeInTheDocument()
  })

  it('não deve exibir gráficos de produtividade ou métricas semanais', () => {
    vi.mocked(githubService.useGithubData).mockReturnValue({
      data: {
        generatedAt: new Date().toISOString(),
        issues: { open: 0, closed: 0 },
        milestones: [],
        features: [],
        burndownData: [],
        commitsByDay: []
      } as any,
      loading: false,
      error: false
    })

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )

    // O texto que antes existia nos títulos dos gráficos removidos
    expect(screen.queryByText('Produtividade Individual')).not.toBeInTheDocument()
    expect(screen.queryByText('Métricas Semanais')).not.toBeInTheDocument()
  })
})
