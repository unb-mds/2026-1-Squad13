import { AlertTriangle } from 'lucide-react'
import type { MilestoneStatus } from '@/entities/sprint'
import { ProgressBar } from '@/shared/ui/progress-bar'
import { useGithubData } from '@/shared/api/github-data-service'
import { Skeleton } from '@/shared/ui/skeleton'

const MILESTONE_COLORS: Record<MilestoneStatus, { text: string; dot: string }> = {
  completed: { text: 'text-green-400', dot: 'bg-green-400' },
  active: { text: 'text-blue-400', dot: 'bg-blue-400 animate-pulse' },
  upcoming: { text: 'text-slate-500', dot: 'bg-slate-600' },
}

export function RoadmapPage() {
  const { data: gh, loading, error } = useGithubData()

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4">
        <AlertTriangle className="w-10 h-10 text-red-500" />
        <p className="text-white font-bold">Erro ao carregar roadmap</p>
      </div>
    )
  }

  const milestones = gh?.milestones || []

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-xl font-bold text-white">Roadmap</h1>
        <p className="text-sm text-slate-500 mt-0.5">Sprints e milestones sincronizados com GitHub</p>
      </div>

      {/* Milestones */}
      <div>
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">Milestones Reais</p>
        <div className="relative">
          <div className="absolute left-3.5 top-0 bottom-0 w-px bg-border-subtle" />
          <div className="space-y-4">
            {loading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="pl-10 space-y-2">
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-20 w-full" />
                </div>
              ))
            ) : milestones.length > 0 ? (
              milestones.map(m => {
                const isClosed = m.state === 'closed'
                const total = m.openIssues + m.closedIssues
                const progress = total > 0 ? Math.round((m.closedIssues / total) * 100) : 0
                const status: MilestoneStatus = isClosed ? 'completed' : progress > 0 ? 'active' : 'upcoming'
                const colors = MILESTONE_COLORS[status]

                return (
                  <div key={m.id} className="flex items-start gap-4 pl-2">
                    <div className={`w-4 h-4 rounded-full ${colors.dot} mt-1 shrink-0 ring-4 ring-surface-0`} />
                    <div className="flex-1 bg-surface-2 border border-border-subtle rounded-xl p-4">
                      <div className="flex items-center justify-between mb-1">
                        <p className={`text-sm font-semibold ${colors.text}`}>{m.title}</p>
                        <span className="text-xs text-slate-500">
                          {m.dueOn ? new Date(m.dueOn).toLocaleDateString('pt-BR') : 'Sem data'}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mb-3">{m.description}</p>
                      
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-[10px]">
                          <span className="text-slate-400">{m.closedIssues} de {total} tasks</span>
                          <span className="text-slate-300 font-medium">{progress}%</span>
                        </div>
                        <ProgressBar value={progress} barClassName={isClosed ? 'bg-green-500' : 'bg-blue-500'} />
                      </div>
                    </div>
                  </div>
                )
              })
            ) : (
              <p className="pl-10 text-xs text-slate-500 italic">Nenhum milestone configurado no repositório.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
