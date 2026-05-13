import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { EmptyState } from '../shared/ui/index'

describe('EmptyState', () => {
  it('renderiza o title fornecido', () => {
    render(<EmptyState title="Nenhum resultado encontrado" />)
    expect(screen.getByText('Nenhum resultado encontrado')).toBeInTheDocument()
  })

  it('renderiza description quando fornecida', () => {
    render(<EmptyState title="Vazio" description="Tente ajustar os filtros." />)
    expect(screen.getByText('Tente ajustar os filtros.')).toBeInTheDocument()
  })

  it('não renderiza description quando omitida', () => {
    render(<EmptyState title="Vazio" />)
    expect(screen.queryByText('Tente ajustar os filtros.')).toBeNull()
  })

  it('renderiza o conteúdo do icon quando fornecido', () => {
    render(<EmptyState title="Vazio" icon="ícone" />)
    expect(screen.getByText('ícone')).toBeInTheDocument()
  })
})
