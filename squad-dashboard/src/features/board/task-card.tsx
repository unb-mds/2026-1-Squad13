import { Calendar, User } from 'lucide-react'
import type { Task } from '@/entities/task'
import { Badge } from '@/shared/ui/badge'
import { ProgressBar } from '@/shared/ui/progress-bar'
import { PRIORITY_CONFIG, LABEL_CONFIG, formatDate } from '@/shared/lib/utils'
import { mockTeam } from '@/mocks/team'

interface TaskCardProps {
  task: Task
}

export function TaskCard({ task }: TaskCardProps) {
  const priority = PRIORITY_CONFIG[task.priority]
  const assignee = mockTeam.find(m => m.id === task.assigneeId)

  return (
    <div className="bg-surface-3 border border-border-subtle rounded-lg p-3 space-y-2.5 hover:border-border-default transition-all animate-slide-up cursor-default group">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm text-slate-200 font-medium leading-snug group-hover:text-white transition-colors">{task.title}</p>
        <span className={`shrink-0 flex items-center gap-1 text-[10px] font-medium ${priority.color}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${priority.dot}`} />
          {priority.label}
        </span>
      </div>

      <div className="flex flex-wrap gap-1">
        {task.labels.map(l => {
          const cfg = LABEL_CONFIG[l]
          return (
            <Badge key={l} className={`${cfg.bg} ${cfg.text}`}>{cfg.label}</Badge>
          )
        })}
      </div>

      {task.status === 'in_progress' && task.progress > 0 && (
        <ProgressBar value={task.progress} showLabel />
      )}

      <div className="flex items-center justify-between text-xs text-slate-500">
        {assignee && (
          <span className="flex items-center gap-1">
            <User className="w-3 h-3" />
            {assignee.name.split(' ')[0]}
          </span>
        )}
        <span className="flex items-center gap-1">
          <Calendar className="w-3 h-3" />
          {formatDate(task.dueDate)}
        </span>
      </div>
    </div>
  )
}
