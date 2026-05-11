export type SprintStatus = 'completed' | 'active' | 'upcoming'
export type MilestoneStatus = 'completed' | 'active' | 'upcoming'

export interface SprintItem {
  id: string
  title: string
  status: SprintStatus
  startDate: string
  endDate: string
  tasksTotal: number
  tasksDone: number
  features: string[]
}

export interface Milestone {
  id: string
  title: string
  date: string
  status: MilestoneStatus
  description: string
}
