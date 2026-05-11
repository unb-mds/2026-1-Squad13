import { useState } from 'react'
import { Search } from 'lucide-react'
import { MemberCard } from '@/features/team/member-card'
import { mockTeam } from '@/mocks/team'
import { EmptyState } from '@/shared/ui/empty-state'

export function TeamPage() {
  const [search, setSearch] = useState('')

  const filtered = mockTeam.filter(m =>
    m.name.toLowerCase().includes(search.toLowerCase()) ||
    m.role.toLowerCase().includes(search.toLowerCase())
  )

  const totalTasks = mockTeam.reduce((a, m) => a + m.tasksCompleted, 0)
  const totalCommits = mockTeam.reduce((a, m) => a + m.commits, 0)
  const avgProductivity = Math.round(mockTeam.reduce((a, m) => a + m.productivity, 0) / mockTeam.length)

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white">Time</h1>
          <p className="text-sm text-slate-500 mt-0.5">Squad 13 · {mockTeam.length} integrantes</p>
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

      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Tasks Concluídas', value: totalTasks },
          { label: 'Total de Commits', value: totalCommits },
          { label: 'Produtividade Média', value: `${avgProductivity}%` },
        ].map(s => (
          <div key={s.label} className="bg-surface-2 border border-border-subtle rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-white">{s.value}</p>
            <p className="text-xs text-slate-500 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {filtered.length === 0 ? (
        <EmptyState title="Integrante não encontrado" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map(m => <MemberCard key={m.id} member={m} />)}
        </div>
      )}
    </div>
  )
}
