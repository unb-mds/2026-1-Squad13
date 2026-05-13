import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Spinner } from '../shared/ui/index'

describe('Spinner', () => {
  it('renderiza sem quebrar', () => {
    const { container } = render(<Spinner />)
    expect(container.firstChild).not.toBeNull()
  })

  it('renderiza um elemento SVG', () => {
    const { container } = render(<Spinner />)
    expect(container.querySelector('svg')).not.toBeNull()
  })

  it('tem label acessível "Carregando"', () => {
    render(<Spinner />)
    expect(screen.getByRole('status', { name: 'Carregando' })).toBeInTheDocument()
  })
})
