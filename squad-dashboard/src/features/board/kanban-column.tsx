import type { Task, TaskStatus } from '@/entities/task'
import { TaskCard } from './task-card'
import { EmptyState } from '@/shared/ui/empty-state'

interface KanbanColumnProps {
  status: TaskStatus
  label: string
  tasks: Task[]
  accentColor: string
}

export function KanbanColumn({ label, tasks, accentColor }: KanbanColumnProps) {
  return (
    <div className="flex flex-col min-w-[260px] flex-1">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: accentColor }} />
          <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">{label}</span>
        </div>
        <span className="text-xs text-slate-500 bg-white/5 px-2 py-0.5 rounded-full">{tasks.length}</span>
      </div>
      <div className="flex flex-col gap-2 flex-1 min-h-[200px]">
        {tasks.length === 0 ? (
          <EmptyState title="Sem tasks" />
        ) : (
          tasks.map(t => <TaskCard key={t.id} task={t} />)
        )}
      </div>
    </div>
  )
}
