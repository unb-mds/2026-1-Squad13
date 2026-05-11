export type FeatureStatus = 'planned' | 'in_progress' | 'review' | 'done' | 'blocked'

export interface Feature {
  id: string
  name: string
  description: string
  status: FeatureStatus
  progress: number
  tasksTotal: number
  tasksDone: number
  ownerId: string
  blockers: string[]
  startDate: string
  targetDate: string
}
