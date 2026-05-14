import type { Task } from './task'

export interface GithubCommitDay {
  date: string
  commits: number
}

export interface GithubCommitAuthor {
  login: string
  commits: number
}

export interface GithubWeeklyCommit {
  week: string
  commits: number
}

export interface GithubContributor {
  login: string
  commits: number
  prsOpened: number
  prsMerged: number
  avatarUrl: string
}

export interface GithubWorkflowRun {
  name: string
  conclusion: string | null
  status: string
  updatedAt: string
}

export interface GithubData {
  generatedAt: string
  totalCommits: number
  coveragePercent: number
  commitsByDay: GithubCommitDay[]
  commitsByAuthor: GithubCommitAuthor[]
  weeklyCommits: GithubWeeklyCommit[]
  pullRequests: {
    open: number
    merged: number
    closed: number
  }
  issues: {
    open: number
    closed: number
  }
  tasks: Task[]
  features: {
    id: string
    name: string
    progress: number
    tasksTotal: number
    tasksDone: number
    status: 'planned' | 'in_progress' | 'done' | 'blocked'
  }[]
  milestones: {
    id: string
    title: string
    description: string
    state: string
    openIssues: number
    closedIssues: number
    dueOn: string | null
    createdAt: string
    updatedAt: string
  }[]
  burnup: {
    metadata: {
      startDate: string
      release1Date: string
      release2Date: string
      baselineScope: number
      methodology: string
    }
    catalog: {
      id: string
      title: string
      release: string
      status: 'planned' | 'in_progress' | 'done'
      completionDate: string | null
      mappedIssueIds: number[]
    }[]
    series: {
      date: string
      label: string
      plannedScope: number
      deliveredR1: number
      deliveredTotal: number
      idealR1: number
      idealTotal: number
      isFuture: boolean
    }[]
  }
  metrics: {
    scopeChange: number
    throughput: number
    completionRate: number
    avgLeadTime: number
  }
  recentWorkflows: GithubWorkflowRun[]
  contributors: GithubContributor[]
}
