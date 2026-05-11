export type TaskStatus = 'backlog' | 'todo' | 'in_progress' | 'review' | 'done'
export type TaskPriority = 'critical' | 'high' | 'medium' | 'low'
export type TaskLabel = 'feature' | 'bug' | 'chore' | 'docs' | 'test'

export interface Task {
  id: string
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority
  labels: TaskLabel[]
  assigneeId: string
  featureId: string
  dueDate: string
  progress: number
  createdAt: string
}
