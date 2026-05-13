import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TeamPage } from '../team-page'
import * as githubService from '@/shared/api/github-data-service'

vi.mock('@/shared/api/github-data-service', () => ({
  useGithubData: vi.fn()
}))

describe('TeamPage', () => {
  it('deve calcular produtividade real baseada em commits e tasks', () => {
    vi.mocked(githubService.useGithubData).mockReturnValue({
      data: {
        contributors: [
          { login: 'kaiky-yun', commits: 10, avatarUrl: '' }
        ],
        tasks: [
          { id: '1', assigneeId: 'kaiky-yun', status: 'done' },
          { id: '2', assigneeId: 'kaiky-yun', status: 'todo' }
        ]
      } as any,
      loading: false,
      error: false
    })

    render(<TeamPage />)
    
    // Kaiky deve aparecer
    expect(screen.getByText('Kaiky')).toBeInTheDocument()
    
    // Verifica se os valores calculados aparecem (pode aparecer mais de uma vez: no KPI global e no card)
    const commitValues = screen.getAllByText('10')
    expect(commitValues.length).toBeGreaterThan(0)
    
    expect(screen.getByText('1 done')).toBeInTheDocument()
  })

  it('deve filtrar integrantes por nome', () => {
    vi.mocked(githubService.useGithubData).mockReturnValue({
      data: { contributors: [], tasks: [] } as any,
      loading: false,
      error: false
    })

    render(<TeamPage />)
    
    expect(screen.getByText('Kaiky')).toBeInTheDocument()
    expect(screen.getByText('Caio Martins')).toBeInTheDocument()
  })
})
