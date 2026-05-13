import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { DashboardPage } from '../dashboard-page'
import * as githubService from '@/shared/api/github-data-service'

// Mock do hook de dados
vi.mock('@/shared/api/github-data-service', () => ({
  useGithubData: vi.fn()
}))

describe('DashboardPage - Strict Mode', () => {
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
    
    // Verifica se existem skeletons de KPI (são 8 KPIs)
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('deve exibir mensagem de erro quando a API falha', () => {
    vi.mocked(githubService.useGithubData).mockReturnValue({
      data: null,
      loading: false,
      error: true
    })

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )

    expect(screen.getByText('Falha ao carregar dados')).toBeInTheDocument()
    expect(screen.getByText(/Não foi possível recuperar as métricas/)).toBeInTheDocument()
  })

  it('deve exibir "N/A" ou 0 quando os dados estão vazios (Strict Mode)', () => {
    vi.mocked(githubService.useGithubData).mockReturnValue({
      data: null,
      loading: false,
      error: false
    })

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )

    // Verifica um KPI que deve mostrar 0 ou N/A
    expect(screen.getByText('Tasks Concluídas')).toBeInTheDocument()
    // O valor default quando gh é null é 0
    const values = screen.getAllByText('0')
    expect(values.length).toBeGreaterThan(0)
  })
})
