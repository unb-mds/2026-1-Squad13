import { useState } from 'react'
import { Search } from 'lucide-react'
import type { TaskStatus, TaskPriority } from '@/entities/task'
import { KanbanColumn } from '@/features/board/kanban-column'
import { mockTasks } from '@/mocks/tasks'

const COLUMNS: { status: TaskStatus; label: string; color: string }[] = [
  { status: 'backlog', label: 'Backlog', color: '#64748b' },
  { status: 'todo', label: 'A Fazer', color: '#3b82f6' },
  { status: 'in_progress', label: 'Em Progresso', color: '#f59e0b' },
  { status: 'review', label: 'Review', color: '#8b5cf6' },
  { status: 'done', label: 'Concluído', color: '#10b981' },
]

export function BoardPage() {
  const [search, setSearch] = useState('')
  const [priorityFilter, setPriorityFilter] = useState<TaskPriority | 'all'>('all')

  const filtered = mockTasks.filter(t => {
    const matchSearch = t.title.toLowerCase().includes(search.toLowerCase())
    const matchPriority = priorityFilter === 'all' || t.priority === priorityFilter
    return matchSearch && matchPriority
  })

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white">Board do Squad</h1>
          <p className="text-sm text-slate-500 mt-0.5">Kanban — Sprint 2 · Consulta e Detalhamento</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
            <input
              type="text"
              placeholder="Buscar task..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="bg-surface-3 border border-border-subtle rounded-lg pl-8 pr-3 py-1.5 text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:border-blue-500/50 w-44"
            />
          </div>
          <select
            value={priorityFilter}
            onChange={e => setPriorityFilter(e.target.value as TaskPriority | 'all')}
            className="bg-surface-3 border border-border-subtle rounded-lg px-3 py-1.5 text-sm text-slate-300 focus:outline-none focus:border-blue-500/50"
          >
            <option value="all">Todas</option>
            <option value="critical">Crítica</option>
            <option value="high">Alta</option>
            <option value="medium">Média</option>
            <option value="low">Baixa</option>
          </select>
        </div>
      </div>

      <div className="flex gap-4 overflow-x-auto pb-4">
        {COLUMNS.map(col => (
          <KanbanColumn
            key={col.status}
            status={col.status}
            label={col.label}
            accentColor={col.color}
            tasks={filtered.filter(t => t.status === col.status)}
          />
        ))}
      </div>
    </div>
  )
}
