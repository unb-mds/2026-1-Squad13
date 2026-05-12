import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Badge } from '../shared/ui/index'

describe('Badge', () => {
  it('renderiza o texto passado como children', () => {
    render(<Badge>Em tramitação</Badge>)
    expect(screen.getByText('Em tramitação')).toBeInTheDocument()
  })

  it('renderiza como elemento span', () => {
    render(<Badge>Elemento</Badge>)
    expect(screen.getByText('Elemento').tagName).toBe('SPAN')
  })

  it('renderiza com variante padrão implícita sem erros', () => {
    render(<Badge>Padrão</Badge>)
    expect(screen.getByText('Padrão')).toBeInTheDocument()
  })

  it('renderiza com variante success sem erros', () => {
    render(<Badge variant="success">Concluído</Badge>)
    expect(screen.getByText('Concluído')).toBeInTheDocument()
  })
})
