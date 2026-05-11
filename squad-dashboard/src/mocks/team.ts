import type { Member } from '@/entities/member'

/**
 * Para atualizar os integrantes: edite o array abaixo.
 * Cada campo editável está comentado com instruções.
 *
 * avatarColor: qualquer cor hex — define o avatar e accent do card.
 * avatarInitials: 2 letras para o avatar (ex: "KA", "MS").
 * currentFocus: texto livre, descreve no que o membro está trabalhando agora.
 */
export const mockTeam: Member[] = [
  {
    id: 'm1',
    name: 'Kaiky',                          // <- edite o nome aqui
    role: 'Cloud/Infra/Arquitetura',
    avatarInitials: 'KA',                   // <- iniciais do avatar
    avatarColor: '#8b5cf6',                 // <- cor accent (hex)
    tasksCompleted: 9,
    tasksPending: 3,
    prsOpened: 4,
    prsMerged: 4,
    commits: 22,
    productivity: 90,
    currentFocus: 'CI/CD, CORS e Arquitetura Layered',
  },
  {
    id: 'm2',
    name: 'Integrante 2',                   // <- edite o nome aqui
    role: 'Frontend Dev',
    avatarInitials: 'I2',
    avatarColor: '#3b82f6',
    tasksCompleted: 4,
    tasksPending: 4,
    prsOpened: 1,
    prsMerged: 1,
    commits: 14,
    productivity: 76,
    currentFocus: 'Consulta de Proposições — UI e estado',
  },
  {
    id: 'm3',
    name: 'Integrante 3',                   // <- edite o nome aqui
    role: 'Backend Dev',
    avatarInitials: 'I3',
    avatarColor: '#10b981',
    tasksCompleted: 6,
    tasksPending: 4,
    prsOpened: 2,
    prsMerged: 2,
    commits: 16,
    productivity: 82,
    currentFocus: 'Endpoint GET /proposicoes/{id}',
  },
  {
    id: 'm4',
    name: 'Integrante 4',                   // <- edite o nome aqui
    role: 'QA/Documentação',
    avatarInitials: 'I4',
    avatarColor: '#f59e0b',
    tasksCompleted: 2,
    tasksPending: 4,
    prsOpened: 1,
    prsMerged: 1,
    commits: 8,
    productivity: 68,
    currentFocus: 'Testes unitários e documentação OpenAPI',
  },
  {
    id: 'm5',
    name: 'Integrante 5',                   // <- edite o nome aqui
    role: 'Produto/Scrum',
    avatarInitials: 'I5',
    avatarColor: '#06b6d4',
    tasksCompleted: 1,
    tasksPending: 2,
    prsOpened: 0,
    prsMerged: 0,
    commits: 4,
    productivity: 62,
    currentFocus: 'Refinamento backlog — predições e dashboard',
  },
]
