import { describe, it, expect } from 'vitest'
import {
  temAtrasoSignificativo,
  formatarTempo,
  paginar,
  corStatus,
  calcularDiasEntreatas,
} from '../shared/lib/utils'

describe('temAtrasoSignificativo', () => {
  it('retorna false para atraso abaixo do limite', () => {
    expect(temAtrasoSignificativo(179)).toBe(false)
  })

  it('retorna false para atraso exatamente no limite', () => {
    expect(temAtrasoSignificativo(180)).toBe(false)
  })

  it('retorna true para atraso acima do limite', () => {
    expect(temAtrasoSignificativo(181)).toBe(true)
  })
})

describe('formatarTempo', () => {
  it('retorna dias quando menor que 30', () => {
    expect(formatarTempo(15)).toBe('15 dias')
  })

  it('retorna meses quando entre 30 e 364 dias', () => {
    expect(formatarTempo(60)).toBe('2 meses')
  })

  it('retorna 1 ano no singular', () => {
    expect(formatarTempo(365)).toBe('1 ano')
  })

  it('retorna anos no plural sem meses restantes', () => {
    expect(formatarTempo(730)).toBe('2 anos')
  })

  it('retorna anos e meses quando há resto', () => {
    expect(formatarTempo(400)).toBe('1 ano e 1 mês')
  })
})

describe('paginar', () => {
  const lista = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

  it('retorna os primeiros itens na página 1', () => {
    expect(paginar(lista, 1, 5)).toEqual([1, 2, 3, 4, 5])
  })

  it('retorna os itens corretos na página 2', () => {
    expect(paginar(lista, 2, 5)).toEqual([6, 7, 8, 9, 10])
  })

  it('retorna apenas os itens restantes na última página parcial', () => {
    expect(paginar(lista, 3, 5)).toEqual([11])
  })
})

describe('corStatus', () => {
  it('retorna classes corretas para status conhecido', () => {
    expect(corStatus('Aprovada')).toBe(
      'bg-volt-400/20 text-volt-300 border-volt-400/30'
    )
  })
})

describe('calcularDiasEntreatas', () => {
  it('calcula a diferença em dias entre duas datas ISO', () => {
    expect(calcularDiasEntreatas('2025-01-01', '2025-04-11')).toBe(100)
  })

  it('retorna 0 quando as duas datas são iguais', () => {
    expect(calcularDiasEntreatas('2025-06-15', '2025-06-15')).toBe(0)
  })
})
