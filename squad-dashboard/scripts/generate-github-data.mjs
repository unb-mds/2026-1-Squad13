import { writeFileSync, mkdirSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const REPO = 'unb-mds/2026-1-Squad13'
const TOKEN = process.env.GITHUB_TOKEN

const HEADERS = {
  'Accept': 'application/vnd.github+json',
  'X-GitHub-Api-Version': '2022-11-28',
  ...(TOKEN ? { 'Authorization': `Bearer ${TOKEN}` } : {}),
}

async function gh(path) {
  const res = await fetch(`https://api.github.com${path}`, { headers: HEADERS })
  if (!res.ok) throw new Error(`GitHub API ${path} → ${res.status} ${res.statusText}`)
  return res.json()
}

function formatDatePtBR(isoDate) {
  const d = new Date(isoDate + 'T12:00:00Z')
  const months = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
  return `${d.getUTCDate().toString().padStart(2, '0')}/${months[d.getUTCMonth()]}`
}

async function main() {
  console.log(`Fetching GitHub data for ${REPO}`)
  if (!TOKEN) console.warn('No GITHUB_TOKEN — using unauthenticated (60 req/h limit)')

  // 1. Recent commits (last 100)
  const commits = await gh(`/repos/${REPO}/commits?per_page=100`)
  console.log(`  commits: ${commits.length}`)

  // Commits by day — last 7 days
  const today = new Date()
  const commitsByDay = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(today)
    d.setUTCDate(d.getUTCDate() - (6 - i))
    const dateStr = d.toISOString().slice(0, 10)
    const count = commits.filter(c => c.commit.author.date.slice(0, 10) === dateStr).length
    return { date: formatDatePtBR(dateStr), commits: count }
  })

  // Commits by author
  const authorMap = {}
  for (const c of commits) {
    const login = c.author?.login ?? c.commit.author.name
    authorMap[login] = (authorMap[login] ?? 0) + 1
  }
  const commitsByAuthor = Object.entries(authorMap)
    .map(([login, count]) => ({ login, commits: count }))
    .sort((a, b) => b.commits - a.commits)

  // Weekly commits — last 8 weeks
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

  // 3. Issues (excluding PRs)
  const allIssues = await gh(`/repos/${REPO}/issues?state=all&per_page=100`)
  const issuesOnly = allIssues.filter(i => !i.pull_request)
  console.log(`  issues: ${issuesOnly.length}`)
  const issues = {
    open: issuesOnly.filter(i => i.state === 'open').length,
    closed: issuesOnly.filter(i => i.state === 'closed').length,
  }

  // 4. Recent workflow runs
  let recentWorkflows = []
  try {
    const runs = await gh(`/repos/${REPO}/actions/runs?per_page=10`)
    recentWorkflows = runs.workflow_runs.map(r => ({
      name: r.name,
      conclusion: r.conclusion,
      status: r.status,
      updatedAt: r.updated_at,
    }))
    console.log(`  workflow runs: ${recentWorkflows.length}`)
  } catch (e) {
    console.warn(`  workflow runs unavailable: ${e.message}`)
  }

  // 5. Contributors
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

  const output = {
    generatedAt: new Date().toISOString(),
    totalCommits: commits.length,
    commitsByDay,
    commitsByAuthor,
    weeklyCommits,
    pullRequests,
    issues,
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
