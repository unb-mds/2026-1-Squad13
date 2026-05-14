import { writeFileSync, mkdirSync, readFileSync, existsSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

/**
 * Script de Automação de Dados do Dashboard
 * ----------------------------------------
 * Este script é o motor de dados do Squad Dashboard. Ele consome a API REST do GitHub
 * para gerar um payload JSON (github-stats.json) contendo métricas reais de engenharia.
 */

const __dirname = dirname(fileURLToPath(import.meta.url))
const REPO = 'unb-mds/2026-1-Squad13'
const TOKEN = process.env.GITHUB_TOKEN

async function gh(path) {
  const headers = { 'Accept': 'application/vnd.github+json' }
  if (TOKEN) headers['Authorization'] = `token ${TOKEN}`
  
  const res = await fetch(`https://api.github.com${path}`, { headers })
  if (!res.ok) throw new Error(`GitHub API error: ${res.status} ${res.statusText}`)
  return res.json()
}

const formatDatePtBR = (iso) => {
  const d = new Date(iso)
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' }).replace('.', '')
}

async function main() {
  console.log(`Fetching GitHub data for ${REPO}`)
  if (!TOKEN) console.warn('No GITHUB_TOKEN — using unauthenticated (60 req/h limit)')

  const today = new Date()
  
  // 1. Commits — last 30 days
  const commits = await gh(`/repos/${REPO}/commits?since=${new Date(Date.now() - 30*24*60*60*1000).toISOString()}&per_page=100`)
  console.log(`  commits: ${commits.length}`)

  const FEATURE_KEYWORDS = {
    'f1': ['proposicao', 'consulta', 'api-camara', 'api-senado', 'adapter'],
    'f2': ['detalhamento', 'detalhe'],
    'f3': ['dashboard', 'kpi', 'chart', 'grafico', 'squad-dashboard'],
    'f5': ['auth', 'login', 'autenticacao'],
    'f6': ['backend', 'infra', 'database', 'docker', 'sqlmodel', 'fastapi', 'architecture', 'arq'],
    'f7': ['test', 'ci', 'workflow', 'ruff', 'pytest', 'vitest', 'lint', 'coverage']
  }

  const featureHistory = {}
  commits.forEach(c => {
    const msg = c.commit.message.toLowerCase()
    const date = new Date(c.commit.author.date)
    const login = c.author?.login ?? c.commit.author.name
    
    Object.entries(FEATURE_KEYWORDS).forEach(([fid, keys]) => {
      if (keys.some(k => msg.includes(k))) {
        if (!featureHistory[fid]) featureHistory[fid] = { first: date, last: date, authors: {} }
        if (date < featureHistory[fid].first) featureHistory[fid].first = date
        if (date > featureHistory[fid].last) featureHistory[fid].last = date
        featureHistory[fid].authors[login] = (featureHistory[fid].authors[login] ?? 0) + 1
      }
    })
  })

  const getFeatureOwner = (fid) => {
    const authors = featureHistory[fid]?.authors
    if (!authors) return 'unassigned'
    return Object.entries(authors).sort((a, b) => b[1] - a[1])[0][0]
  }

  const commitsByDay = Array.from({ length: 8 }, (_, i) => {
    const d = new Date(today)
    d.setDate(today.getDate() - i)
    const dateStr = d.toISOString().slice(0, 10)
    const count = commits.filter(c => c.commit.author.date.slice(0, 10) === dateStr).length
    return { date: formatDatePtBR(dateStr), commits: count }
  }).reverse()

  const authorMap = {}
  for (const c of commits) {
    const login = c.author?.login ?? c.commit.author.name
    authorMap[login] = (authorMap[login] ?? 0) + 1
  }
  const commitsByAuthor = Object.entries(authorMap)
    .map(([login, count]) => ({ login, commits: count }))
    .sort((a, b) => b.commits - a.commits)

  // 2. Pull requests
  const allPRs = await gh(`/repos/${REPO}/pulls?state=all&per_page=100`)
  const pullRequests = {
    open: allPRs.filter(pr => pr.state === 'open').length,
    merged: allPRs.filter(pr => !!pr.merged_at).length,
    closed: allPRs.filter(pr => pr.state === 'closed' && !pr.merged_at).length,
  }

  const prStatsByAuthor = {}
  allPRs.forEach(pr => {
    const login = pr.user.login
    if (!prStatsByAuthor[login]) prStatsByAuthor[login] = { opened: 0, merged: 0 }
    prStatsByAuthor[login].opened++
    if (pr.merged_at) prStatsByAuthor[login].merged++
  })

  // 3. Issues and Burnup calculation
  const allIssues = await gh(`/repos/${REPO}/issues?state=all&per_page=100`)
  const issuesOnly = allIssues.filter(i => !i.pull_request)
  
  const issues = {
    open: issuesOnly.filter(i => i.state === 'open').length,
    closed: issuesOnly.filter(i => i.state === 'closed').length,
  }

  // --- CONFIGURAÇÃO DO BURNUP BASEADO EM ENTREGÁVEIS (STORY MAP) ---
  const DAY_ZERO = '2026-05-11'
  const RELEASE_1_DATE = '2026-05-27'
  const RELEASE_2_DATE = '2026-07-06'

  const STORY_MAP_CATALOG = [
    { id: 'R1-1', title: 'Busca e Filtros Reais (Backend)', release: 'R1', feat: 'f1', keywords: ['ilike', 'busca', 'filtro'] },
    { id: 'R1-2', title: 'Endpoint Detalhe /proposicoes/{id}', release: 'R1', feat: 'f1', keywords: ['get /proposicoes/{id}', 'detalhe real'] },
    { id: 'R1-3', title: 'Dossiê com Dados Reais', release: 'R1', feat: 'f2', keywords: ['tempo de tramitação', 'dados reais'] },
    { id: 'R1-4', title: 'Autenticação JWT (Login)', release: 'R1', feat: 'f5', keywords: ['jwt', 'login', 'auth/login'] },
    { id: 'R1-5', title: 'Cadastro de Usuários', release: 'R1', feat: 'f5', keywords: ['cadastro', 'usuarios/cadastro'] },
    { id: 'R1-6', title: 'Seed de Dados Reais (Idempotente)', release: 'R1', feat: 'f6', keywords: ['seed', 'init_db', 'popular'] },
    { id: 'R1-7', title: 'Correção SenadoAdapter (Movimentação)', release: 'R1', feat: 'f6', keywords: ['senadoadapter', 'ultima_movimentacao'] },
    { id: 'R1-8', title: 'Infraestrutura de Testes (Vitest/Pytest)', release: 'R1', feat: 'f7', keywords: ['test', 'vitest', 'pytest'] },
    { id: 'R2-1', title: 'Entidade e Timeline de Tramitação', release: 'R2', feat: 'f2', keywords: ['timeline', 'movimentacoes', 'tramitacao'] },
    { id: 'R2-2', title: 'Breakdown de Tempo por Fase', release: 'R2', feat: 'f2', keywords: ['tempo por fase', 'comissão'] },
    { id: 'R2-3', title: 'Dashboard Real (Endpoints Agregação)', release: 'R2', feat: 'f3', keywords: ['dashboard/por-', 'breakdown'] },
    { id: 'R2-4', title: 'Filtros Globais no Dashboard', release: 'R2', feat: 'f3', keywords: ['filtros ativos', 'dashboard'] },
    { id: 'R2-5', title: 'Logout com Invalidação (Server-side)', release: 'R2', feat: 'f5', keywords: ['logout', 'blacklist', 'redis'] },
    { id: 'R2-6', title: 'Recuperação de Senha (E-mail)', release: 'R2', feat: 'f5', keywords: ['recuperar', 'senha', 'email'] },
    { id: 'R2-7', title: 'Bloqueio de Conta (Segurança)', release: 'R2', feat: 'f5', keywords: ['bloqueio', 'tentativas'] },
    { id: 'R2-8', title: 'Worker de Coleta Batch (Celery)', release: 'R2', feat: 'f6', keywords: ['worker', 'celery', 'batch', 'coleta'] },
    { id: 'R2-9', title: 'Cache Redis para Métricas', release: 'R2', feat: 'f6', keywords: ['cache', 'redis'] },
    { id: 'R2-10', title: 'Inteligência Preditiva (IA)', release: 'R2', feat: 'f4', keywords: ['preditiva', 'ia', 'previsao'] }
  ]

  const catalogWithProgress = STORY_MAP_CATALOG.map(item => {
    const mappedIssues = issuesOnly.filter(i => {
      const labels = i.labels.map(l => l.name.toLowerCase())
      const title = i.title.toLowerCase()
      const body = (i.body || '').toLowerCase()
      const matchFeat = labels.includes(`feat:${item.feat}`)
      const matchKeyword = item.keywords.some(k => title.includes(k) || body.includes(k))
      const matchExplicitId = title.includes(`[${item.id}]`) || body.includes(`[${item.id}]`)
      return matchExplicitId || (matchFeat && matchKeyword)
    })
    const closedIssues = mappedIssues.filter(i => i.state === 'closed')
    const isDone = closedIssues.length > 0
    const completionDate = isDone 
      ? closedIssues.sort((a, b) => new Date(b.closed_at) - new Date(a.closed_at))[0].closed_at.slice(0, 10)
      : null
    return {
      ...item,
      status: isDone ? 'done' : mappedIssues.length > 0 ? 'in_progress' : 'planned',
      completionDate,
      mappedIssueIds: mappedIssues.map(i => i.number)
    }
  })

  const burnupSeries = []
  const start = new Date(DAY_ZERO)
  const end = new Date(today > new Date(RELEASE_2_DATE) ? today : RELEASE_2_DATE)
  const diffDays = (d1, d2) => Math.ceil((new Date(d2) - new Date(d1)) / (1000 * 60 * 60 * 24))
  const totalDaysR1 = diffDays(DAY_ZERO, RELEASE_1_DATE)
  const totalDaysR2 = diffDays(DAY_ZERO, RELEASE_2_DATE)
  const scopeR1 = STORY_MAP_CATALOG.filter(i => i.release === 'R1').length
  const scopeTotal = STORY_MAP_CATALOG.length

  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const dateStr = d.toISOString().slice(0, 10)
    if (d > today && dateStr > RELEASE_2_DATE) break
    const daysPassed = diffDays(DAY_ZERO, dateStr)
    const isFuture = d > today
    const deliveredR1 = isFuture ? null : catalogWithProgress.filter(i => i.release === 'R1' && i.status === 'done' && i.completionDate <= dateStr).length
    const deliveredTotal = isFuture ? null : catalogWithProgress.filter(i => i.status === 'done' && i.completionDate <= dateStr).length
    const idealR1 = (dateStr <= RELEASE_1_DATE && daysPassed <= totalDaysR1)
      ? Number(((scopeR1 / totalDaysR1) * daysPassed).toFixed(2)) 
      : null
    const idealTotal = (dateStr <= RELEASE_2_DATE && daysPassed <= totalDaysR2)
      ? Number(((scopeTotal / totalDaysR2) * daysPassed).toFixed(2)) 
      : null
    burnupSeries.push({
      date: dateStr,
      label: d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
      plannedScope: scopeTotal,
      deliveredR1,
      deliveredTotal,
      idealR1,
      idealTotal,
      isFuture: d > today
    })
  }

  const burnupMetadata = {
    startDate: DAY_ZERO,
    release1Date: RELEASE_1_DATE,
    release2Date: RELEASE_2_DATE,
    baselineScope: scopeTotal,
    methodology: "Burnup baseado em catálogo fixo do Story Map. O progresso é contabilizado apenas quando issues mapeadas para entregáveis reais são fechadas."
  }

  // 4. Tasks and Features
  const tasks = issuesOnly.map(i => {
    const labels = i.labels.map(l => l.name)
    let status = 'todo'
    if (labels.includes('status:backlog')) status = 'backlog'
    else if (labels.includes('status:todo')) status = 'todo'
    else if (labels.includes('status:in_progress')) status = 'in_progress'
    else if (labels.includes('status:review')) status = 'review'
    else if (labels.includes('status:done') || i.state === 'closed') status = 'done'
    else if (i.state === 'open' && i.assignee) status = 'in_progress'

    let priority = 'medium'
    if (labels.includes('prio:critical')) priority = 'critical'
    else if (labels.includes('prio:high')) priority = 'high'
    else if (labels.includes('prio:low')) priority = 'low'

    const taskLabels = []
    if (labels.includes('bug')) taskLabels.push('bug')
    if (labels.includes('documentation')) taskLabels.push('docs')
    if (labels.includes('enhancement')) taskLabels.push('feature')
    if (labels.includes('test')) taskLabels.push('test')
    if (taskLabels.length === 0) taskLabels.push('chore')

    const taskFid = i.labels?.find(l => l.name && l.name.startsWith('feat:'))?.name.replace('feat:', '') || 'general'
    const realTaskStart = featureHistory[taskFid]?.first ? featureHistory[taskFid].first.toISOString().slice(0, 10) : i.created_at.slice(0, 10)
    let assigneeId = i.assignee?.login || 'unassigned'
    if (assigneeId === 'unassigned' && taskFid !== 'general') assigneeId = getFeatureOwner(taskFid)

    return {
      id: String(i.number),
      title: i.title,
      description: i.body || '',
      status,
      priority,
      labels: taskLabels,
      assigneeId,
      featureId: taskFid,
      dueDate: i.milestone?.due_on?.slice(0, 10) || '',
      progress: (status === 'done' || i.state === 'closed') ? 100 : 0,
      createdAt: (realTaskStart < i.created_at.slice(0, 10)) ? realTaskStart : i.created_at.slice(0, 10),
      url: i.html_url
    }
  })

  const featureNames = {
    'f1': 'Consulta de Proposições',
    'f2': 'Detalhamento da Proposição',
    'f3': 'Dashboard Analítico',
    'f4': 'Inteligência Preditiva',
    'f5': 'Autenticação',
    'f6': 'Infraestrutura & Arquitetura',
    'f7': 'Qualidade & CI/CD'
  }

  const features = Object.entries(featureNames).map(([id, name]) => {
    const featureTasks = tasks.filter(t => t.featureId === id)
    const tasksTotal = featureTasks.length
    const tasksDone = featureTasks.filter(t => t.status === 'done').length
    const progress = tasksTotal > 0 ? Math.round((tasksDone / tasksTotal) * 100) : 0
    return { id, name, progress, tasksTotal, tasksDone, status: progress === 100 ? 'done' : progress > 0 ? 'in_progress' : 'planned' }
  })

  // 5. Contributors and Workflows (simpler)
  let recentWorkflows = []
  try {
    const runs = await gh(`/repos/${REPO}/actions/runs?per_page=10`)
    recentWorkflows = (runs.workflow_runs || []).map(r => ({ name: r.name, conclusion: r.conclusion, status: r.status, updatedAt: r.updated_at }))
  } catch (e) {}

  let contributors = []
  try {
    const stats = await gh(`/repos/${REPO}/contributors?per_page=20`)
    if (Array.isArray(stats)) {
      contributors = stats.map(c => ({ login: c.login, commits: c.contributions, avatarUrl: c.avatar_url }))
    }
  } catch (e) {}

  const output = {
    generatedAt: new Date().toISOString(),
    totalCommits: commits.length,
    commitsByDay,
    pullRequests,
    issues,
    tasks,
    features,
    milestones: [],
    burnup: {
      metadata: burnupMetadata,
      catalog: catalogWithProgress,
      series: burnupSeries
    },
    metrics: {
      scopeChange: 0,
      throughput: Math.round((catalogWithProgress.filter(i => i.status === 'done').length / 15) * 10) / 10,
      completionRate: Math.round((catalogWithProgress.filter(i => i.status === 'done').length / scopeTotal) * 100),
      avgLeadTime: 0,
    },
    recentWorkflows,
    contributors: contributors.map(c => ({ 
      login: c.login, 
      commits: c.commits, 
      prsOpened: prStatsByAuthor[c.login]?.opened || 0,
      prsMerged: prStatsByAuthor[c.login]?.merged || 0,
      avatarUrl: c.avatarUrl 
    }))
  }

  const outDir = join(__dirname, '..', 'public', 'data')
  mkdirSync(outDir, { recursive: true })
  writeFileSync(join(outDir, 'github-stats.json'), JSON.stringify(output, null, 2))
  console.log('\nDone → public/data/github-stats.json')
}

main().catch(e => { console.error(e.message); process.exit(1) })
