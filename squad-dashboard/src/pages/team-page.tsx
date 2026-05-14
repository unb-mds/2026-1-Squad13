import { useState, useMemo } from 'react'
import { Search, AlertTriangle } from 'lucide-react'
import { MemberCard } from '@/features/team/member-card'
import { mockTeam } from '@/mocks/team'
import { EmptyState } from '@/shared/ui/empty-state'
import { useGithubData } from '@/shared/api/github-data-service'
import { Skeleton } from '@/shared/ui/skeleton'

export function TeamPage() {
  const [search, setSearch] = useState('')
  const { data: gh, loading, error } = useGithubData()

  const realTeam = useMemo(() => {
    if (!gh) return mockTeam

    return mockTeam.map(member => {
      const contributor = gh.contributors.find(c => c.login === member.login)
      const memberTasks = gh.tasks.filter(t => t.assigneeId === member.login || t.assigneeId === member.id)
      
      const tasksCompleted = memberTasks.filter(t => t.status === 'done').length
      const tasksPending = memberTasks.length - tasksCompleted
      const commits = contributor?.commits ?? 0
      const prsOpened = contributor?.prsOpened ?? 0
      const prsMerged = contributor?.prsMerged ?? 0
      
      // Basic productivity score: (commits * 1.5) + (tasks * 10) capped at 100
      const productivity = Math.min(100, (commits * 1.5) + (tasksCompleted * 10))

      return {
        ...member,
        commits,
        tasksCompleted,
        tasksPending,
        prsOpened,
        prsMerged,
        productivity: Math.round(productivity),
      }
    })
  }, [gh])

  const filtered = realTeam.filter(m =>
    m.name.toLowerCase().includes(search.toLowerCase()) ||
    m.role.toLowerCase().includes(search.toLowerCase())
  )

  const totalTasks = realTeam.reduce((a, m) => a + m.tasksCompleted, 0)
  const totalCommits = realTeam.reduce((a, m) => a + m.commits, 0)
  const avgProductivity = realTeam.length > 0 
    ? Math.round(realTeam.reduce((a, m) => a + m.productivity, 0) / realTeam.length)
    : 0

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4">
        <AlertTriangle className="w-10 h-10 text-red-500" />
        <p className="text-white font-bold">Erro ao carregar dados do time</p>
      </div>
    )
  }

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white">Time</h1>
          <p className="text-sm text-slate-500 mt-0.5">Squad 13 · {realTeam.length} integrantes</p>
        </div>
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
          <input
            type="text"
            placeholder="Buscar integrante..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="bg-surface-3 border border-border-subtle rounded-lg pl-8 pr-3 py-1.5 text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:border-blue-500/50 w-44"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label: 'Tasks Concluídas', value: loading ? <Skeleton className="h-8 w-12 mx-auto" /> : totalTasks },
          { label: 'Total de Commits', value: loading ? <Skeleton className="h-8 w-12 mx-auto" /> : totalCommits },
          { label: 'Produtividade Média', value: loading ? <Skeleton className="h-8 w-12 mx-auto" /> : `${avgProductivity}%` },
        ].map(s => (
          <div key={s.label} className="bg-surface-2 border border-border-subtle rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-white mb-1">{s.value}</div>
            <p className="text-xs text-slate-500 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-surface-2 border border-border-subtle rounded-xl p-5 h-48">
              <Skeleton className="h-full w-full" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState title="Integrante não encontrado" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map(m => <MemberCard key={m.id} member={m} />)}
        </div>
      )}
    </div>
  )
}
