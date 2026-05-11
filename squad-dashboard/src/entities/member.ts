export type MemberRole =
  | 'Cloud/Infra/Arquitetura'
  | 'Frontend Dev'
  | 'Backend Dev'
  | 'Full Stack'
  | 'QA/Documentação'
  | 'Produto/Scrum'

export interface Member {
  id: string
  name: string
  role: MemberRole
  avatarInitials: string
  avatarColor: string
  tasksCompleted: number
  tasksPending: number
  prsOpened: number
  prsMerged: number
  commits: number
  productivity: number
  currentFocus: string
}
