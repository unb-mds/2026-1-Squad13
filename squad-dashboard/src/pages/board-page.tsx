import { useState, useEffect, useMemo } from 'react'
import { Search, RotateCcw, Save, Settings, X, Loader2, CheckCircle2, AlertCircle, GripVertical } from 'lucide-react'
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragStartEvent,
  DragOverEvent,
  DragEndEvent,
  defaultDropAnimationSideEffects,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'

import type { Task, TaskStatus, TaskPriority } from '@/entities/task'
import { KanbanColumn } from '@/features/board/kanban-column'
import { TaskCard } from '@/features/board/task-card'
import { mockTasks } from '@/mocks/tasks'
import { useGithubData } from '@/shared/api/github-data-service'

const COLUMNS: { status: TaskStatus; label: string; color: string }[] = [
  { status: 'backlog', label: 'Backlog', color: '#64748b' },
  { status: 'todo', label: 'A Fazer', color: '#3b82f6' },
  { status: 'in_progress', label: 'Em Progresso', color: '#f59e0b' },
  { status: 'review', label: 'Review', color: '#8b5cf6' },
  { status: 'done', label: 'Concluído', color: '#10b981' },
]

type SyncStatus = 'idle' | 'saving' | 'success' | 'error'

export function BoardPage() {
  const { data: gh, loading: dataLoading } = useGithubData()
  const [tasks, setTasks] = useState<Task[]>([])
  const [originalTasks, setOriginalTasks] = useState<Task[]>([])
  const [activeTask, setActiveTask] = useState<Task | null>(null)
  
  const [search, setSearch] = useState('')
  const [priorityFilter, setPriorityFilter] = useState<TaskPriority | 'all'>('all')

  // Config & Sync state
  const [showSettings, setShowSettings] = useState(false)
  const [token, setToken] = useState(localStorage.getItem('gh_token') || '')
  const [repo, setRepo] = useState(localStorage.getItem('gh_repo') || 'unb-mds/2026-1-Squad13')
  const [syncStatus, setSyncStatus] = useState<SyncStatus>('idle')
  const [syncError, setSyncError] = useState('')

  useEffect(() => {
    if (!dataLoading) {
      const initialTasks = gh?.tasks || mockTasks
      setTasks(initialTasks)
      setOriginalTasks(initialTasks)
    }
  }, [gh, dataLoading])

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  )

  const filteredTasks = useMemo(() => {
    return tasks.filter(t => {
      const matchSearch = t.title.toLowerCase().includes(search.toLowerCase())
      const matchPriority = priorityFilter === 'all' || t.priority === priorityFilter
      return matchSearch && matchPriority
    })
  }, [tasks, search, priorityFilter])

  const hasChanges = useMemo(() => {
    return tasks.some(t => {
      const original = originalTasks.find(ot => ot.id === t.id)
      return original && original.status !== t.status
    })
  }, [tasks, originalTasks])

  function handleDragStart(event: DragStartEvent) {
    const { active } = event
    const task = tasks.find(t => t.id === active.id)
    if (task) setActiveTask(task)
  }

  function handleDragOver(event: DragOverEvent) {
    const { active, over } = event
    if (!over) return

    const activeId = active.id
    const overId = over.id
    if (activeId === overId) return

    const isActiveATask = active.data.current?.type === 'Task'
    const isOverATask = over.data.current?.type === 'Task'
    const isOverAColumn = over.data.current?.type === 'Column'

    if (!isActiveATask) return

    if (isOverATask) {
      setTasks(prev => {
        const activeIndex = prev.findIndex(t => t.id === activeId)
        const overIndex = prev.findIndex(t => t.id === overId)

        if (prev[activeIndex].status !== prev[overIndex].status) {
          const updated = [...prev]
          updated[activeIndex] = { ...updated[activeIndex], status: prev[overIndex].status }
          return arrayMove(updated, activeIndex, overIndex)
        }
        return arrayMove(prev, activeIndex, overIndex)
      })
    }

    if (isOverAColumn) {
      setTasks(prev => {
        const activeIndex = prev.findIndex(t => t.id === activeId)
        const newStatus = over.id as TaskStatus
        if (prev[activeIndex].status !== newStatus) {
          const updated = [...prev]
          updated[activeIndex] = { ...updated[activeIndex], status: newStatus }
          return arrayMove(updated, activeIndex, activeIndex)
        }
        return prev
      })
    }
  }

  function handleDragEnd(event: DragEndEvent) {
    setActiveTask(null)
    const { active, over } = event
    if (!over) return
    const activeId = active.id
    const overId = over.id
    if (activeId === overId) return

    setTasks(prev => {
      const activeIndex = prev.findIndex(t => t.id === activeId)
      const overIndex = prev.findIndex(t => t.id === overId)
      return arrayMove(prev, activeIndex, overIndex)
    })
  }

  const saveSettings = () => {
    localStorage.setItem('gh_token', token)
    localStorage.setItem('gh_repo', repo)
    setShowSettings(false)
  }

  const handleSaveToGithub = async () => {
    if (!token) {
      setShowSettings(true)
      return
    }

    setSyncStatus('saving')
    setSyncError('')

    const changedTasks = tasks.filter(t => {
      const original = originalTasks.find(ot => ot.id === t.id)
      return original && original.status !== t.status
    })

    try {
      for (const task of changedTasks) {
        const res = await fetch(`https://api.github.com/repos/${repo}/issues/${task.id}`, {
          headers: { 'Authorization': `Bearer ${token}`, 'Accept': 'application/vnd.github+json' }
        })
        if (!res.ok) throw new Error(`Erro ao buscar issue #${task.id}`)
        const issueData = await res.json()
        const otherLabels = issueData.labels.map((l: any) => l.name).filter((l: string) => !l.startsWith('status:'))
        const finalLabels = [...otherLabels, `status:${task.status}`]
        
        const patchRes = await fetch(`https://api.github.com/repos/${repo}/issues/${task.id}`, {
          method: 'PATCH',
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ labels: finalLabels, state: task.status === 'done' ? 'closed' : 'open' })
        })
        if (!patchRes.ok) throw new Error(`Erro ao atualizar issue #${task.id}`)
      }
      setSyncStatus('success')
      setOriginalTasks([...tasks])
      setTimeout(() => setSyncStatus('idle'), 3000)
    } catch (err: any) {
      setSyncStatus('error')
      setSyncError(err.message || 'Erro ao sincronizar')
    }
  }

  return (
    <div className="space-y-5 animate-fade-in pb-10">
      {showSettings && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-surface-2 border border-border-subtle rounded-2xl w-full max-w-md shadow-2xl">
            <div className="p-5 border-b border-border-subtle flex items-center justify-between">
              <h2 className="text-lg font-bold text-white flex items-center gap-2"><Settings className="w-5 h-5 text-blue-400" /> Configurações</h2>
              <button onClick={() => setShowSettings(false)} className="text-slate-500 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-5 space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-500 uppercase">Repositório</label>
                <input value={repo} onChange={e => setRepo(e.target.value)} className="w-full bg-surface-3 border border-border-subtle rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500/50" />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-500 uppercase">Token GitHub</label>
                <input type="password" value={token} onChange={e => setToken(e.target.value)} className="w-full bg-surface-3 border border-border-subtle rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500/50" placeholder="ghp_..." />
              </div>
            </div>
            <div className="p-5 bg-surface-1/50 flex justify-end gap-3 rounded-b-2xl">
              <button onClick={() => setShowSettings(false)} className="px-4 py-2 text-sm text-slate-400">Cancelar</button>
              <button onClick={saveSettings} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg font-medium">Salvar</button>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            Board do Squad {gh && <span className="text-[10px] bg-blue-500/20 text-blue-400 px-1.5 py-0.5 rounded border border-blue-500/30">LIVE</span>}
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">{gh ? 'Dados reais do GitHub' : 'Sprint 2 · Consulta e Detalhamento'}</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
            <input type="text" placeholder="Buscar..." value={search} onChange={e => setSearch(e.target.value)} className="bg-surface-3 border border-border-subtle rounded-lg pl-8 pr-3 py-1.5 text-sm text-slate-300 w-44 focus:outline-none focus:border-blue-500/50" />
          </div>
          <select value={priorityFilter} onChange={e => setPriorityFilter(e.target.value as any)} className="bg-surface-3 border border-border-subtle rounded-lg px-3 py-1.5 text-sm text-slate-300 focus:outline-none">
            <option value="all">Prioridade</option>
            <option value="critical">Crítica</option>
            <option value="high">Alta</option>
            <option value="medium">Média</option>
            <option value="low">Baixa</option>
          </select>
          <button onClick={() => setTasks(gh?.tasks || mockTasks)} className="p-1.5 bg-surface-3 border border-border-subtle rounded-lg text-slate-400 hover:text-white" title="Resetar"><RotateCcw className="w-4 h-4" /></button>
        </div>
      </div>

      <DndContext sensors={sensors} collisionDetection={closestCorners} onDragStart={handleDragStart} onDragOver={handleDragOver} onDragEnd={handleDragEnd}>
        <div className="flex gap-4 overflow-x-auto pb-4 min-h-[500px]">
          {COLUMNS.map(col => (
            <KanbanColumn key={col.status} status={col.status} label={col.label} accentColor={col.color} tasks={filteredTasks.filter(t => t.status === col.status)} />
          ))}
        </div>
        <DragOverlay dropAnimation={{ sideEffects: defaultDropAnimationSideEffects({ styles: { active: { opacity: '0.5' } } }) }}>
          {activeTask ? <TaskCard task={activeTask} isOverlay /> : null}
        </DragOverlay>
      </DndContext>

      <div className="fixed bottom-6 right-6 flex items-center gap-3 z-40">
        {syncStatus === 'error' && <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-lg text-xs flex items-center gap-2"><AlertCircle className="w-4 h-4" /> {syncError}</div>}
        <button onClick={() => setShowSettings(true)} className="bg-surface-3 border border-border-subtle p-3 rounded-full text-slate-400 hover:text-white shadow-xl hover:border-blue-500/50"><Settings className={`w-5 h-5 ${token ? 'text-green-500/70' : ''}`} /></button>
        <button onClick={handleSaveToGithub} disabled={syncStatus === 'saving' || (!hasChanges && syncStatus !== 'error')} className={`px-6 py-3 rounded-full shadow-xl flex items-center gap-2 font-bold transition-all transform hover:scale-105 active:scale-95 ${hasChanges ? 'bg-blue-600 hover:bg-blue-500 text-white' : 'bg-surface-3 text-slate-500 border border-border-subtle cursor-not-allowed'} ${syncStatus === 'saving' ? 'bg-blue-600/50 animate-pulse' : ''} ${syncStatus === 'success' ? 'bg-green-600 text-white' : ''}`}>
          {syncStatus === 'saving' ? <><Loader2 className="w-5 h-5 animate-spin" /> Sincronizando...</> : syncStatus === 'success' ? <><CheckCircle2 className="w-5 h-5" /> Sincronizado!</> : <><Save className="w-5 h-5" /> {hasChanges ? 'Salvar no GitHub' : 'Sem mudanças'}</>}
        </button>
      </div>
    </div>
  )
}