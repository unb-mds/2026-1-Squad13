import { writeFileSync, mkdirSync, readFileSync, existsSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

/**
 * Script de Automação de Dados do Dashboard
 * ----------------------------------------
 * Este script é o motor de dados do Squad Dashboard. Ele consome a API REST do GitHub
 * para gerar um payload JSON (github-stats.json) contendo métricas reais de engenharia.
 * 
 * Principais funcionalidades:
 * 1. Extração de série temporal de Commits (últimos 8 dias e 8 semanas).
 * 2. Mapeamento de Issues para Entidades de Tarefa (Task).
 * 3. Cálculo de Burndown Real baseado no saldo histórico de issues abertas.
 * 4. Cálculo de progresso de Features baseado em labels (ex: feat:f1).
 * 5. Monitoramento de Workflows de CI e Contribuições por autor.
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

  // --- LOGICA DE FIDELIDADE HISTORICA & AUTO-CREDIT ---
  const FEATURE_KEYWORDS = {
    'f1': ['proposicao', 'consulta', 'api-camara', 'api-senado', 'adapter'],
    'f2': ['detalhamento', 'detalhe'],
    'f3': ['dashboard', 'kpi', 'chart', 'grafico', 'squad-dashboard'],
    'f5': ['auth', 'login', 'autenticacao'],
    'f6': ['backend', 'infra', 'database', 'docker', 'sqlmodel', 'fastapi', 'architecture', 'arq'],
    'f7': ['test', 'ci', 'workflow', 'ruff', 'pytest', 'vitest', 'lint', 'coverage']
  }

  const featureHistory = {} // { fid: { first: Date, last: Date, authors: { login: count } } }
  
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

  // Helper para decidir o "dono" de uma feature baseado no volume de commits
  const getFeatureOwner = (fid) => {
    const authors = featureHistory[fid]?.authors
    if (!authors) return 'unassigned'
    return Object.entries(authors).sort((a, b) => b[1] - a[1])[0][0]
  }
  // ---------------------------------------------------------------------

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

  const weeklyCommits = Array.from({ length: 8 }, (_, i) => {
    const weekEnd = new Date(today)
    weekEnd.setUTCDate(weekEnd.getUTCDate() - i * 7)
    const weekStart = new Date(weekEnd)
    weekStart.setUTCDate(weekEnd.getUTCDate() - 6)
    const count = commits.filter(c => {
      const d = new Date(c.commit.author.date)
      return d >= weekStart && d <= weekEnd
    }).length
    return { week: `W${8 - i}`, commits: count }
  }).reverse()

  // 2. Pull requests
  const allPRs = await gh(`/repos/${REPO}/pulls?state=all&per_page=100`)
  console.log(`  PRs: ${allPRs.length}`)
  const pullRequests = {
    open: allPRs.filter(pr => pr.state === 'open').length,
    merged: allPRs.filter(pr => !!pr.merged_at).length,
    closed: allPRs.filter(pr => pr.state === 'closed' && !pr.merged_at).length,
  }

  // 3. Issues and Burndown calculation
  const allIssues = await gh(`/repos/${REPO}/issues?state=all&per_page=100`)
  const issuesOnly = allIssues.filter(i => !i.pull_request)
  console.log(`  issues: ${issuesOnly.length}`)
  
  const issues = {
    open: issuesOnly.filter(i => i.state === 'open').length,
    closed: issuesOnly.filter(i => i.state === 'closed').length,
  }

  const burndownData = []
  const daysToShow = 20
  for (let i = daysToShow; i >= 0; i--) {
    const targetDate = new Date(today)
    targetDate.setDate(today.getDate() - i)
    const dateStr = targetDate.toISOString().slice(0, 10)
    
    const openOnDate = issuesOnly.filter(i => {
      const fid = i.labels?.find(l => l.name && l.name.startsWith('feat:'))?.name.replace('feat:', '')
      const realStart = featureHistory[fid]?.first ? featureHistory[fid].first.toISOString().slice(0, 10) : null
      
      const created = (realStart && realStart < i.created_at.slice(0, 10)) ? realStart : i.created_at.slice(0, 10)
      const closed = i.closed_at ? i.closed_at.slice(0, 10) : '9999-12-31'
      return created <= dateStr && closed > dateStr
    }).length

    burndownData.push({
      day: targetDate.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' }),
      remaining: openOnDate,
      ideal: Math.max(0, Math.round(issuesOnly.length - (issuesOnly.length / daysToShow) * (daysToShow - i)))
    })
  }

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
    
    // Auto-Credit: Se não houver assignee, tenta encontrar o dono da feature via commits
    let assigneeId = i.assignee?.login || 'unassigned'
    if (assigneeId === 'unassigned' && taskFid !== 'general') {
      assigneeId = getFeatureOwner(taskFid)
    }

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
      progress: (status === 'done' || i.state === 'closed') ? 100 : status === 'in_progress' ? 50 : 0,
      createdAt: (realTaskStart < i.created_at.slice(0, 10)) ? realTaskStart : i.created_at.slice(0, 10),
      url: i.html_url
    }
    })

  // 4. Milestones
  let milestones = []
  try {
    const rawMilestones = await gh(`/repos/${REPO}/milestones?state=all&sort=due_on&direction=asc`)
    milestones = (rawMilestones || []).map(m => ({
      id: String(m.id),
      title: m.title,
      description: m.description || '',
      state: m.state,
      openIssues: m.open_issues,
      closedIssues: m.closed_issues,
      dueOn: m.due_on,
      createdAt: m.created_at,
      updatedAt: m.updated_at,
    }))
    console.log(`  milestones: ${milestones.length}`)
  } catch (e) {
    console.warn(`  milestones unavailable: ${e.message}`)
  }

  // 5. Feature progress calculation
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
    
    return {
      id,
      name,
      progress,
      tasksTotal,
      tasksDone,
      status: progress === 100 ? 'done' : progress > 0 ? 'in_progress' : 'planned'
    }
  })

  // 6. Recent workflow runs
  let recentWorkflows = []
  try {
    const runs = await gh(`/repos/${REPO}/actions/runs?per_page=10`)
    recentWorkflows = (runs.workflow_runs || []).map(r => ({
      name: r.name,
      conclusion: r.conclusion,
      status: r.status,
      updatedAt: r.updated_at,
    }))
    console.log(`  workflow runs: ${recentWorkflows.length}`)
  } catch (e) {
    console.warn(`  workflow runs unavailable: ${e.message}`)
  }

  // 7. Contributors
  let contributors = []
  try {
    const stats = await gh(`/repos/${REPO}/contributors?per_page=20`)
    if (Array.isArray(stats)) {
      contributors = stats.map(c => ({
        login: c.login,
        commits: c.contributions,
        avatarUrl: c.avatar_url,
      }))
      console.log(`  contributors: ${contributors.length}`)
    }
  } catch (e) {
    console.warn(`  contributors unavailable: ${e.message}`)
  }

  // 8. Cobertura de Código (Opcional)
  let coveragePercent = 0
  const coveragePath = join(__dirname, '../coverage/coverage-summary.json')
  if (existsSync(coveragePath)) {
    try {
      const summary = JSON.parse(readFileSync(coveragePath, 'utf8'))
      coveragePercent = summary.total?.statements?.pct || 0
      console.log(`  coverage: ${coveragePercent}%`)
    } catch (e) {
      console.warn('  erro ao ler coverage-summary.json')
    }
  }

  const output = {
    generatedAt: new Date().toISOString(),
    totalCommits: commits.length,
    coveragePercent,
    commitsByDay,
    commitsByAuthor,
    weeklyCommits,
    pullRequests,
    issues,
    tasks,
    features,
    milestones,
    burndownData,
    recentWorkflows,
    contributors,
  }

  const outDir = join(__dirname, '..', 'public', 'data')
  mkdirSync(outDir, { recursive: true })
  writeFileSync(join(outDir, 'github-stats.json'), JSON.stringify(output, null, 2))

  console.log('\nDone → public/data/github-stats.json')
  console.log(`  PRs merged: ${pullRequests.merged} | open: ${pullRequests.open}`)
  console.log(`  Issues open: ${issues.open} | closed: ${issues.closed}`)
}

main().catch(e => { console.error(e.message); process.exit(1) })
