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
  recentWorkflows: GithubWorkflowRun[]
  contributors: GithubContributor[]
}
