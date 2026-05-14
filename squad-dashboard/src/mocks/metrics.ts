export interface WeeklyMetric {
  week: string
  completed: number
  added: number
  velocity: number
}

export interface CommitDay {
  date: string
  commits: number
}

export interface BurnupPoint {
  date: string
  label: string
  plannedScope: number
  deliveredR1: number
  deliveredTotal: number
  idealR1: number
  idealTotal: number
  isFuture: boolean
}

export const mockWeeklyMetrics: WeeklyMetric[] = [
  { week: 'S1 W1', completed: 3, added: 6,  velocity: 50 },
  { week: 'S1 W2', completed: 4, added: 2,  velocity: 68 },
  { week: 'S1 W3', completed: 5, added: 3,  velocity: 74 },
  { week: 'S1 W4', completed: 3, added: 1,  velocity: 72 },
  { week: 'S2 W1', completed: 2, added: 5,  velocity: 58 },
  { week: 'S2 W2', completed: 2, added: 2,  velocity: 62 },
]

export const mockCommitsByDay: CommitDay[] = [
  { date: '05/mai', commits: 6  },
  { date: '06/mai', commits: 4  },
  { date: '07/mai', commits: 9  },
  { date: '08/mai', commits: 3  },
  { date: '09/mai', commits: 7  },
  { date: '10/mai', commits: 2  },
  { date: '11/mai', commits: 5  },
]

export const mockBurnupSeries: BurnupPoint[] = [
  { date: '2026-05-11', label: '11 Mai', plannedScope: 18, deliveredR1: 0, deliveredTotal: 0, idealR1: 0, idealTotal: 0, isFuture: false },
  { date: '2026-05-15', label: '15 Mai', plannedScope: 18, deliveredR1: 2, deliveredTotal: 2, idealR1: 2, idealTotal: 1, isFuture: false },
]

export const mockKpis = {
  totalTasks: 25,
  tasksDone: 12,
  tasksInProgress: 3,
  bugsOpen: 0,
  weeklyVelocity: 62,
  prsMerged: 5,
  coveragePercent: 28,
  overallProgress: 32,
}
