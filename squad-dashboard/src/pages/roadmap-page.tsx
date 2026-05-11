import { CheckCircle2, Circle, Clock, Layers } from 'lucide-react'
import { mockSprints, mockMilestones } from '@/mocks/sprints'
import type { SprintStatus, MilestoneStatus } from '@/entities/sprint'
import { ProgressBar } from '@/shared/ui/progress-bar'

const SPRINT_COLORS: Record<SprintStatus, string> = {
  completed: 'text-green-400 border-green-500/30 bg-green-500/10',
  active: 'text-blue-400 border-blue-500/30 bg-blue-500/10',
  upcoming: 'text-slate-400 border-border-subtle bg-surface-3',
}

const MILESTONE_COLORS: Record<MilestoneStatus, { text: string; dot: string }> = {
  completed: { text: 'text-green-400', dot: 'bg-green-400' },
  active: { text: 'text-blue-400', dot: 'bg-blue-400 animate-pulse' },
  upcoming: { text: 'text-slate-500', dot: 'bg-slate-600' },
}

const StatusIcon = ({ status }: { status: SprintStatus }) => {
  if (status === 'completed') return <CheckCircle2 className="w-4 h-4 text-green-400" />
  if (status === 'active') return <Clock className="w-4 h-4 text-blue-400" />
  return <Circle className="w-4 h-4 text-slate-600" />
}

export function RoadmapPage() {
  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-xl font-bold text-white">Roadmap</h1>
        <p className="text-sm text-slate-500 mt-0.5">Sprints e milestones do projeto</p>
      </div>

      {/* Milestones */}
      <div>
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">Milestones</p>
        <div className="relative">
          <div className="absolute left-3.5 top-0 bottom-0 w-px bg-border-subtle" />
          <div className="space-y-4">
            {mockMilestones.map(m => {
              const colors = MILESTONE_COLORS[m.status]
              return (
                <div key={m.id} className="flex items-start gap-4 pl-2">
                  <div className={`w-4 h-4 rounded-full ${colors.dot} mt-1 shrink-0 ring-4 ring-surface-0`} />
                  <div className="flex-1 bg-surface-2 border border-border-subtle rounded-xl p-4">
                    <div className="flex items-center justify-between mb-1">
                      <p className={`text-sm font-semibold ${colors.text}`}>{m.title}</p>
                      <span className="text-xs text-slate-500">{new Date(m.date).toLocaleDateString('pt-BR')}</span>
                    </div>
                    <p className="text-xs text-slate-500">{m.description}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Sprints */}
      <div>
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">Sprints</p>
        <div className="space-y-4">
          {mockSprints.map(s => {
            const pct = Math.round((s.tasksDone / s.tasksTotal) * 100)
            return (
              <div key={s.id} className={`border rounded-xl p-5 ${SPRINT_COLORS[s.status]}`}>
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div className="flex items-center gap-3">
                    <StatusIcon status={s.status} />
                    <div>
                      <p className="text-sm font-semibold text-white">{s.title}</p>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {new Date(s.startDate).toLocaleDateString('pt-BR')} → {new Date(s.endDate).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                  <span className="text-sm font-bold tabular-nums">{pct}%</span>
                </div>

                <div className="space-y-3">
                  <ProgressBar
                    value={pct}
                    barClassName={s.status === 'completed' ? 'bg-green-500' : s.status === 'active' ? 'bg-blue-500' : 'bg-slate-600'}
                  />
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>{s.tasksDone} de {s.tasksTotal} tasks</span>
                    <span className={s.status === 'active' ? 'text-blue-400' : ''}>
                      {s.status === 'completed' ? 'Concluído' : s.status === 'active' ? 'Em andamento' : 'Planejado'}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {s.features.map(f => (
                      <span key={f} className="inline-flex items-center gap-1 text-[10px] bg-white/5 border border-border-subtle px-2 py-0.5 rounded-full text-slate-400">
                        <Layers className="w-2.5 h-2.5" />
                        {f}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
