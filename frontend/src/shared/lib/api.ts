import { PROPOSICOES_MOCK, getMovimentacoes } from '../lib/mock-data'
import { paginar } from '../lib/utils'
import type {
  Proposicao,
  MovimentacaoTramitacao,
  MetricasDashboard,
  DadosGraficoTipo,
  DadosGraficoComissao,
  DadosGraficoStatus,
  GargaloInstitucional,
  ComparacaoTema,
  FiltrosProposicao,
} from '../types'

function filtrarMocks(
  items: typeof PROPOSICOES_MOCK,
  filtros: FiltrosProposicao
): typeof PROPOSICOES_MOCK {
  return items.filter((p) => {
    const termo = filtros.busca?.toLowerCase() ?? ''
    const matchBusca =
      !filtros.busca ||
      p.ementa.toLowerCase().includes(termo) ||
      p.numero.toLowerCase().includes(termo) ||
      p.autor.toLowerCase().includes(termo) ||
      p.tags.some((t) => t.toLowerCase().includes(termo))
    const matchOrgao = !filtros.orgaoOrigem || p.orgaoOrigem === filtros.orgaoOrigem
    const matchTipo = !filtros.tipo || p.tipo === filtros.tipo
    const matchStatus = !filtros.status || p.status === filtros.status
    const matchDataInicio = !filtros.dataInicio || p.dataApresentacao >= filtros.dataInicio
    const matchDataFim = !filtros.dataFim || p.dataApresentacao <= filtros.dataFim
    return matchBusca && matchOrgao && matchTipo && matchStatus && matchDataInicio && matchDataFim
  })
}

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const delay = (ms: number) => new Promise((res) => setTimeout(res, ms))

// --- Auth ---
export async function loginApi(email: string, senha: string): Promise<{ token: string; user: { id: string; nome: string; email: string; perfil: 'analista' } }> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password: senha }),
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail || 'Credenciais inválidas. Verifique seu e-mail e senha.')
  }

  const data = await response.json()
  
  return {
    token: data.access_token,
    user: {
      id: String(data.user.id),
      nome: data.user.nome,
      email: data.user.email,
      perfil: data.user.perfil,
    },
  }
}

export async function cadastroApi(nome: string, email: string, senha: string): Promise<{ token: string; user: { id: string; nome: string; email: string; perfil: 'analista' } }> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome, email, password: senha }),
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail || 'Erro ao realizar cadastro.')
  }

  // Após o cadastro, fazemos o login automaticamente para obter o token
  return loginApi(email, senha)
}

export async function recuperarSenhaApi(_email: string): Promise<void> {
  await delay(1200)
}

// --- Proposições ---
export async function listarProposicoes(
  filtros: FiltrosProposicao,
  pagina: number,
  itensPorPagina: number
): Promise<{ items: Proposicao[]; total: number }> {
  const params = new URLSearchParams()

  if (filtros.busca) params.append('busca', filtros.busca)
  if (filtros.tipo) params.append('tipo', filtros.tipo)
  if (filtros.status) params.append('status', filtros.status)
  if (filtros.orgaoOrigem) params.append('orgaoOrigem', filtros.orgaoOrigem)
  if (filtros.dataInicio) params.append('dataInicio', filtros.dataInicio)
  if (filtros.dataFim) params.append('dataFim', filtros.dataFim)
  params.append('pagina', String(pagina))
  params.append('itens_por_pagina', String(itensPorPagina))

  try {
    const response = await fetch(`${API_BASE}/proposicoes?${params.toString()}`)

    if (!response.ok) {
      console.warn('API falhou, usando dados mockados.')
      const filtradas = filtrarMocks(PROPOSICOES_MOCK, filtros)
      const items = paginar(filtradas, pagina, itensPorPagina)
      return { items, total: filtradas.length }
    }

    const data = await response.json()
    return { items: data.items, total: data.total }
  } catch (error) {
    console.warn('Erro ao conectar na API, usando dados mockados:', error)
    const filtradas = filtrarMocks(PROPOSICOES_MOCK, filtros)
    const items = paginar(filtradas, pagina, itensPorPagina)
    return { items, total: filtradas.length }
  }
}

export async function obterProposicao(id: string): Promise<Proposicao | null> {
  try {
    const response = await fetch(`${API_BASE}/proposicoes/${id}`)

    if (!response.ok) {
      console.warn(`API falhou para /proposicoes/${id} (status: ${response.status}), tentando dados mockados.`)
      return PROPOSICOES_MOCK.find((p) => 
        p.id === id || 
        `${p.tipo}-${p.numero}-${p.ano}` === id
      ) ?? null
    }

    return await response.json()
  } catch (error) {
    console.warn('Erro ao conectar na API, usando dados mockados:', error)
    return PROPOSICOES_MOCK.find((p) => 
      p.id === id || 
      `${p.tipo}-${p.numero}-${p.ano}` === id
    ) ?? null
  }
}

export async function obterMovimentacoes(proposicaoId: string): Promise<MovimentacaoTramitacao[]> {
  try {
    const response = await fetch(`${API_BASE}/proposicoes/${proposicaoId}/movimentacoes`)

    if (!response.ok) {
      console.warn(`API falhou para movimentações da proposição ${proposicaoId}, usando dados mockados.`)
      const proposicao = PROPOSICOES_MOCK.find((p) => 
        p.id === proposicaoId || 
        `${p.tipo}-${p.numero}-${p.ano}` === proposicaoId
      )
      if (!proposicao) return []
      return getMovimentacoes(proposicao.id, proposicao)
    }

    const rawData = await response.json()
    // Normalização das propriedades do Backend para a interface do Frontend
    return (rawData as Array<{
      sequencia?: number;
      proposicaoId: string;
      dataHora?: string;
      siglaOrgao?: string;
      descricaoTramitacao?: string;
    }>).map((d, index) => ({
      id: d.sequencia ? String(d.sequencia) : String(index),
      proposicaoId: d.proposicaoId,
      data: d.dataHora || new Date().toISOString(),
      orgao: d.siglaOrgao || 'N/A',
      descricao: d.descricaoTramitacao || 'Tramitação registrada',
      responsavel: undefined,
      diasNaEtapa: 0,
      temAtraso: false,
    }))
  } catch (error) {
    console.warn('Erro ao conectar na API de movimentações, usando dados mockados:', error)
    const proposicao = PROPOSICOES_MOCK.find((p) => 
      p.id === proposicaoId || 
      `${p.tipo}-${p.numero}-${p.ano}` === proposicaoId
    )
    if (!proposicao) return []
    return getMovimentacoes(proposicao.id, proposicao)
  }
}

// --- Dashboard ---
function agruparStatus(statusRaw: string): string {
  const status = statusRaw.toLowerCase()
  if (
    ['aprovada', 'sancionada', 'promulgado', 'norma jurídica', 'enviado à sanção'].some((s) =>
      status.includes(s)
    )
  )
    return 'Aprovada/Sancionada'
  if (
    ['rejeitada', 'arquivada', 'retirada', 'prejudicada', 'indeferida', 'devolvida'].some((s) =>
      status.includes(s)
    )
  )
    return 'Rejeitada/Arquivada'
  return 'Em tramitação'
}

export async function obterMetricas(): Promise<MetricasDashboard> {
  try {
    const response = await fetch(`${API_BASE}/dashboard/metricas`)
    if (!response.ok) throw new Error('Falha ao buscar métricas da API')
    return await response.json()
  } catch (error) {
    console.warn('Usando métricas mockadas devido a erro na API:', error)
    await delay(600)
    const total = PROPOSICOES_MOCK.length
    const aprovadas = PROPOSICOES_MOCK.filter((p) => agruparStatus(p.status) === 'Aprovada/Sancionada').length
    const rejeitadas = PROPOSICOES_MOCK.filter((p) => agruparStatus(p.status) === 'Rejeitada/Arquivada').length
    const emTramitacao = PROPOSICOES_MOCK.filter((p) => agruparStatus(p.status) === 'Em tramitação').length

    return {
      tempoMedioTramitacao: 412,
      totalProposicoes: total,
      proposicoesComAtraso: PROPOSICOES_MOCK.filter((p) => p.temAtraso).length,
      comissaoMaiorTempo: 'CCJ',
      comissaoMaiorTempoMedia: 680,
      totalAprovadas: aprovadas,
      totalEmTramitacao: emTramitacao,
      totalRejeitadas: rejeitadas,
    }
  }
}

export async function obterDadosTipo(): Promise<DadosGraficoTipo[]> {
  try {
    const response = await fetch(`${API_BASE}/dashboard/grafico-tipo`)
    if (!response.ok) throw new Error('Falha ao buscar dados por tipo')
    return await response.json()
  } catch (error) {
    console.warn('Usando dados mockados por tipo devido a erro na API:', error)
    await delay(400)
    return [
      { tipo: 'PL', tempoMedio: 380, quantidade: 7 },
      { tipo: 'PEC', tempoMedio: 477, quantidade: 3 },
      { tipo: 'MP', tempoMedio: 180, quantidade: 1 },
      { tipo: 'PLP', tempoMedio: 43, quantidade: 1 },
    ]
  }
}

export async function obterDadosComissao(): Promise<DadosGraficoComissao[]> {
  try {
    const response = await fetch(`${API_BASE}/dashboard/grafico-comissao`)
    if (!response.ok) throw new Error('Falha ao buscar dados por comissão')
    return await response.json()
  } catch (error) {
    console.warn('Usando dados mockados por comissão devido a erro na API:', error)
    await delay(400)
    return [
      { comissao: 'CCJ', tempoMedio: 680, quantidade: 8 },
      { comissao: 'CFT', tempoMedio: 510, quantidade: 5 },
      { comissao: 'CAS', tempoMedio: 390, quantidade: 4 },
      { comissao: 'CMADS', tempoMedio: 340, quantidade: 3 },
      { comissao: 'CTASP', tempoMedio: 295, quantidade: 4 },
      { comissao: 'CDH', tempoMedio: 260, quantidade: 2 },
    ]
  }
}

export async function obterDadosStatus(): Promise<DadosGraficoStatus[]> {
  try {
    const response = await fetch(`${API_BASE}/dashboard/grafico-status`)
    if (!response.ok) throw new Error('Falha ao buscar dados por status')
    return await response.json()
  } catch (error) {
    console.warn('Usando dados mockados por status devido a erro na API:', error)
    await delay(300)
    const total = PROPOSICOES_MOCK.length
    const contagem: Record<string, number> = {}
    
    PROPOSICOES_MOCK.forEach((p) => {
      const statusAgrupado = agruparStatus(p.status)
      contagem[statusAgrupado] = (contagem[statusAgrupado] ?? 0) + 1
    })

    return Object.entries(contagem)
      .map(([status, quantidade]) => ({
        status,
        quantidade,
        percentual: Math.round((quantidade / total) * 100),
      }))
      .sort((a, b) => b.quantidade - a.quantidade)
  }
}

// --- Relatórios ---
export async function obterGargalos(): Promise<GargaloInstitucional[]> {
  try {
    const response = await fetch(`${API_BASE}/dashboard/gargalos`)
    if (!response.ok) throw new Error('Falha ao buscar gargalos da API')
    return await response.json()
  } catch (error) {
    console.warn('Usando gargalos mockados devido a erro na API:', error)
    await delay(500)
    return [
      { orgao: 'CCJ', tempoMedioMeses: 22, quantidadeProposicoes: 8, taxaAtraso: 62 },
      { orgao: 'CFT', tempoMedioMeses: 17, quantidadeProposicoes: 5, taxaAtraso: 40 },
      { orgao: 'CAS', tempoMedioMeses: 13, quantidadeProposicoes: 4, taxaAtraso: 25 },
      { orgao: 'CMADS', tempoMedioMeses: 11, quantidadeProposicoes: 3, taxaAtraso: 33 },
      { orgao: 'Plenário Câmara', tempoMedioMeses: 18, quantidadeProposicoes: 6, taxaAtraso: 50 },
    ]
  }
}

export async function obterComparacaoTemas(): Promise<ComparacaoTema[]> {
  await delay(400)
  return [
    { tema: 'Tributário', tempoMedioDias: 215, taxaAprovacao: 78, velocidade: 'rapido' },
    { tema: 'Educação', tempoMedioDias: 380, taxaAprovacao: 55, velocidade: 'medio' },
    { tema: 'Tecnologia & IA', tempoMedioDias: 310, taxaAprovacao: 42, velocidade: 'medio' },
    { tema: 'Reforma Administrativa', tempoMedioDias: 920, taxaAprovacao: 18, velocidade: 'lento' },
    { tema: 'Previdência', tempoMedioDias: 266, taxaAprovacao: 70, velocidade: 'rapido' },
    { tema: 'Internet & Mídia', tempoMedioDias: 1322, taxaAprovacao: 12, velocidade: 'lento' },
    { tema: 'Trabalho & Emprego', tempoMedioDias: 538, taxaAprovacao: 60, velocidade: 'medio' },
    { tema: 'Meio Ambiente', tempoMedioDias: 726, taxaAprovacao: 30, velocidade: 'lento' },
  ]
}
