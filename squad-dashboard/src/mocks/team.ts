import type { Member } from '@/entities/member'

/**
 * Substituir estes placeholders pelos nomes reais dos integrantes quando definidos.
 *
 * Para atualizar: edite o campo `name` e `avatarInitials` de cada entrada.
 * Os IDs (m1…m5) são referenciados em tasks.ts e features.ts — não altere os IDs.
 *
 * avatarColor: qualquer cor hex — define o avatar e accent do card.
 * avatarInitials: 2 letras para o avatar (ex: "KA", "FL").
 * currentFocus: texto livre — o que o membro está trabalhando agora.
 */
export const mockTeam: Member[] = [
  {
    id: 'm1',
    name: 'Kaiky',                          // <- nome real
    role: 'Cloud/Infra/Arquitetura',
    avatarInitials: 'KA',
    avatarColor: '#8b5cf6',
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
    name: 'Frontend Lead',                  // <- substituir pelo nome real
    role: 'Frontend Dev',
    avatarInitials: 'FL',
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
    name: 'Backend Lead',                   // <- substituir pelo nome real
    role: 'Backend Dev',
    avatarInitials: 'BL',
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
    name: 'QA/Docs',                        // <- substituir pelo nome real
    role: 'QA/Documentação',
    avatarInitials: 'QD',
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
    name: 'Product/Scrum',                  // <- substituir pelo nome real
    role: 'Produto/Scrum',
    avatarInitials: 'PS',
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
