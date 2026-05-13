import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ProposicaoCard } from '../features/proposicoes/ProposicaoCard'
import type { Proposicao } from '../shared/types'

// Mock do useNavigate pois o componente usa react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  }
})

const proposicaoBase: Proposicao = {
  id: '1',
  tipo: 'PL',
  numero: '123',
  ano: 2024,
  ementa: 'Ementa completa',
  ementaResumida: 'Ementa resumida',
  autor: 'Autor Teste',
  orgaoOrigem: 'Câmara',
  status: 'Em tramitação',
  orgaoAtual: 'CCJ',
  dataApresentacao: '2024-01-01',
  dataUltimaMovimentacao: '2024-01-01',
  tempoTotalDias: 100,
  temAtraso: false,
  atrasoCritico: false,
  temPrevisaoIA: false,
  tags: ['teste'],
}

describe('ProposicaoCard', () => {
  it('renderiza informações básicas corretamente', () => {
    render(
      <MemoryRouter>
        <ProposicaoCard proposicao={proposicaoBase} />
      </MemoryRouter>
    )

    expect(screen.getByText('PL')).toBeDefined()
    expect(screen.getByText('123/2024')).toBeDefined()
    expect(screen.getByText('Ementa resumida')).toBeDefined()
  })

  it('exibe badge de Atraso Crítico quando a propriedade está ativa', () => {
    const propComAtraso = { ...proposicaoBase, atrasoCritico: true }
    
    render(
      <MemoryRouter>
        <ProposicaoCard proposicao={propComAtraso} />
      </MemoryRouter>
    )

    expect(screen.getByText('Atraso Crítico')).toBeDefined()
  })

  it('não exibe badge de Atraso Crítico quando a propriedade está inativa', () => {
    render(
      <MemoryRouter>
        <ProposicaoCard proposicao={proposicaoBase} />
      </MemoryRouter>
    )

    const badge = screen.queryByText('Atraso Crítico')
    expect(badge).toBeNull()
  })
})
