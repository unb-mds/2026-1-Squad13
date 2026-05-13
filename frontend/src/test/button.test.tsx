import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Button } from '../shared/ui/index'

describe('Button', () => {
  it('renderiza o texto passado como children', () => {
    render(<Button>Salvar</Button>)
    expect(screen.getByText('Salvar')).toBeInTheDocument()
  })

  it('renderiza como elemento button', () => {
    render(<Button>Elemento</Button>)
    expect(screen.getByRole('button').tagName).toBe('BUTTON')
  })

  it('aplica disabled quando disabled é true', () => {
    render(<Button disabled>Desabilitado</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('aplica disabled quando loading é true', () => {
    render(<Button loading>Carregando</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
