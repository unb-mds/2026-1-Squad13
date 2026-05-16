export const TIPOS_PROPOSICAO = ['PL', 'PEC'] as const

export const STATUS_PROPOSICAO = [
  'Em tramitação',
  'Aprovada',
  'Relatoria',
  'Norma Jurídica',
  'Aguardando',
  'Pauta',
  'Redação Final',
  'Prejudicado',
  'Retirada',
] as const

export const ORGAOS = [
  'Câmara dos Deputados',
  'Senado Federal',
  'CCJ',
  'CAS',
  'CAE',
  'CFT',
  'CTASP',
  'CMADS',
  'CDH',
  'CMA',
] as const

export const ITENS_POR_PAGINA = 10

export const DIAS_ATRASO_SIGNIFICATIVO = 180

export const AUTH_TOKEN_KEY = 'lex_token'
export const AUTH_USER_KEY = 'lex_user'
export const AUTH_EXPIRES_KEY = 'lex_expires'

export const TOKEN_EXPIRATION_MS = 1000 * 60 * 60 * 8 // 8 horas

export const DISCLAIMER_IA =
  'A estimativa é baseada em dados históricos e não constitui garantia de aprovação.'
