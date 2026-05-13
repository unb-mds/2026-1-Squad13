import { useDroppable } from '@dnd-kit/core'
import {
  SortableContext,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import type { Task, TaskStatus } from '@/entities/task'
import { TaskCard } from './task-card'
import { EmptyState } from '@/shared/ui/empty-state'

interface KanbanColumnProps {
  status: TaskStatus
  label: string
  tasks: Task[]
  accentColor: string
}

export function KanbanColumn({ status, label, tasks, accentColor }: KanbanColumnProps) {
  const { setNodeRef } = useDroppable({
    id: status,
    data: {
      type: 'Column',
      status,
    },
  })

  return (
    <div ref={setNodeRef} className="flex flex-col min-w-[280px] w-[280px] flex-shrink-0">
      <div className="flex items-center justify-between mb-3 bg-surface-1/50 p-2 rounded-t-lg border-b border-border-subtle">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: accentColor }} />
          <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">{label}</span>
        </div>
        <span className="text-xs text-slate-500 bg-white/5 px-2 py-0.5 rounded-full tabular-nums">{tasks.length}</span>
      </div>
      <div className="flex flex-col gap-2 flex-1 min-h-[500px] bg-surface-1/20 p-2 rounded-b-lg border border-border-subtle border-t-0">
        <SortableContext items={tasks.map(t => t.id)} strategy={verticalListSortingStrategy}>
          {tasks.length === 0 ? (
            <div className="opacity-40 h-24 flex items-center justify-center">
              <EmptyState title="Vazio" />
            </div>
          ) : (
            tasks.map(t => <TaskCard key={t.id} task={t} />)
          )}
        </SortableContext>
      </div>
    </div>
  )
}
