import { Calendar, User, ExternalLink, GripVertical } from 'lucide-react'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import type { Task } from '@/entities/task'
import { Badge } from '@/shared/ui/badge'
import { ProgressBar } from '@/shared/ui/progress-bar'
import { PRIORITY_CONFIG, LABEL_CONFIG, formatDate } from '@/shared/lib/utils'
import { mockTeam } from '@/mocks/team'

interface TaskCardProps {
  task: Task
  isOverlay?: boolean
}

export function TaskCard({ task, isOverlay }: TaskCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: task.id,
    data: {
      type: 'Task',
      task,
    },
  })

  const style = {
    transition,
    transform: CSS.Translate.toString(transform),
  }

  const priority = PRIORITY_CONFIG[task.priority]
  const assignee = mockTeam.find(m => m.id === task.assigneeId || m.login === task.assigneeId)

  if (isDragging) {
    return (
      <div
        ref={setNodeRef}
        style={style}
        className="bg-surface-3/30 border-2 border-dashed border-blue-500/30 rounded-lg p-3 h-[120px] opacity-50"
      />
    )
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`bg-surface-3 border border-border-subtle rounded-lg p-3 space-y-2.5 hover:border-border-default transition-all cursor-default group relative ${
        isOverlay ? 'shadow-2xl border-blue-500/50 scale-105' : 'animate-slide-up'
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2 min-w-0">
          <div {...attributes} {...listeners} className="mt-1 cursor-grab active:cursor-grabbing text-slate-600 hover:text-slate-400">
            <GripVertical className="w-3.5 h-3.5" />
          </div>
          <p className="text-sm text-slate-200 font-medium leading-snug group-hover:text-white transition-colors truncate">
            {task.title}
          </p>
        </div>
        <span className={`shrink-0 flex items-center gap-1 text-[10px] font-medium ${priority.color}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${priority.dot}`} />
          {priority.label}
        </span>
      </div>

      <div className="flex flex-wrap gap-1">
        {task.labels.map(l => {
          const cfg = LABEL_CONFIG[l] || { label: l, bg: 'bg-slate-800', text: 'text-slate-400' }
          return (
            <Badge key={l} className={`${cfg.bg} ${cfg.text}`}>{cfg.label}</Badge>
          )
        })}
        {task.featureId && task.featureId !== 'general' && (
          <Badge className="bg-purple-500/10 text-purple-400 border border-purple-500/20">
            {task.featureId}
          </Badge>
        )}
      </div>

      {task.status === 'in_progress' && task.progress > 0 && (
        <ProgressBar value={task.progress} showLabel />
      )}

      <div className="flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-3">
          {assignee && (
            <span className="flex items-center gap-1">
              <User className="w-3 h-3" />
              {assignee.name.split(' ')[0]}
            </span>
          )}
          {task.dueDate && (
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {formatDate(task.dueDate)}
            </span>
          )}
        </div>
        
        {/* @ts-ignore - url exists in real tasks */}
        {task.url && (
          <a 
            href={task.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-slate-600 hover:text-blue-400 transition-colors p-1"
          >
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>
    </div>
  )
}
