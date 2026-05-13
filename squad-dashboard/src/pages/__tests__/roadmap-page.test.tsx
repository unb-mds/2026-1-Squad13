import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { RoadmapPage } from '../roadmap-page'
import * as githubService from '@/shared/api/github-data-service'

vi.mock('@/shared/api/github-data-service', () => ({
  useGithubData: vi.fn()
}))

describe('RoadmapPage', () => {
  it('deve renderizar milestones reais do GitHub', () => {
    vi.mocked(githubService.useGithubData).mockReturnValue({
      data: {
        milestones: [
          {
            id: '1',
            title: 'Release 1.0',
            description: 'Primeira entrega estável',
            state: 'open',
            openIssues: 5,
            closedIssues: 5,
            dueOn: '2026-05-30T00:00:00Z',
            createdAt: '2026-01-01',
            updatedAt: '2026-05-12'
          }
        ]
      } as any,
      loading: false,
      error: false
    })

    render(<RoadmapPage />)
    
    expect(screen.getByText('Release 1.0')).toBeInTheDocument()
    expect(screen.getByText('Primeira entrega estável')).toBeInTheDocument()
    expect(screen.getByText('50%')).toBeInTheDocument()
    expect(screen.getByText('5 de 10 tasks')).toBeInTheDocument()
  })

  it('deve exibir mensagem quando não houver milestones', () => {
    vi.mocked(githubService.useGithubData).mockReturnValue({
      data: { milestones: [] } as any,
      loading: false,
      error: false
    })

    render(<RoadmapPage />)
    expect(screen.getByText(/Nenhum milestone configurado/)).toBeInTheDocument()
  })
})
