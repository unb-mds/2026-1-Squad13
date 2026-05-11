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

export interface BurndownPoint {
  day: string
  remaining: number
  ideal: number
}

/**
 * Métricas semanais — Sprint 1 (semanas 1-4) e Sprint 2 (semanas 5-7).
 * Baseadas no progresso real observado no repositório.
 */
export const mockWeeklyMetrics: WeeklyMetric[] = [
  { week: 'S1 W1', completed: 3, added: 6,  velocity: 50 }, // setup inicial, muitas tasks abertas
  { week: 'S1 W2', completed: 4, added: 2,  velocity: 68 }, // CI/CD + arquitetura
  { week: 'S1 W3', completed: 5, added: 3,  velocity: 74 }, // endpoint + adapters
  { week: 'S1 W4', completed: 3, added: 1,  velocity: 72 }, // integração frontend
  { week: 'S2 W1', completed: 2, added: 5,  velocity: 58 }, // CORS fix, novas tasks abertas
  { week: 'S2 W2', completed: 2, added: 2,  velocity: 62 }, // review + docs (semana atual)
  { week: 'S2 W3', completed: 0, added: 0,  velocity: 0  }, // ainda não aconteceu
]

/**
 * Commits por dia — últimos 7 dias úteis (Mai/2026).
 * Estimativa baseada no ritmo observado no git log.
 */
export const mockCommitsByDay: CommitDay[] = [
  { date: '05/mai', commits: 6  },
  { date: '06/mai', commits: 4  },
  { date: '07/mai', commits: 9  },
  { date: '08/mai', commits: 3  },
  { date: '09/mai', commits: 7  },
  { date: '10/mai', commits: 2  },
  { date: '11/mai', commits: 5  },
]

/**
 * Burndown do Sprint 2 (10 tasks, 22 dias).
 * Eixo X: dias do sprint. Iniciou em 01/mai, hoje é 11/mai (dia 11).
 * Situação atual: 4 tasks concluídas, 6 restantes → ligeiramente abaixo do ideal.
 */
export const mockBurndown: BurndownPoint[] = [
  { day: 'D1',  remaining: 10, ideal: 10   },
  { day: 'D3',  remaining: 10, ideal: 8.6  },
  { day: 'D5',  remaining: 8,  ideal: 7.3  },
  { day: 'D7',  remaining: 7,  ideal: 5.9  },
  { day: 'D9',  remaining: 7,  ideal: 4.5  },
  { day: 'D11', remaining: 6,  ideal: 3.2  }, // hoje
  { day: 'D14', remaining: -1, ideal: 1.4  }, // projeção
  { day: 'D22', remaining: -1, ideal: 0    }, // fim sprint
]

/**
 * KPIs globais do projeto.
 * Edite aqui para refletir o estado real ao longo do tempo.
 *
 * prsMerged: PRs reais mergeados no repositório (PR #2, #4, #5 + squad-dashboard = 5)
 * coveragePercent: cobertura real de testes (estimativa — atualizar ao rodar pytest/vitest)
 * overallProgress: média ponderada do progresso das features ativas
 */
export const mockKpis = {
  totalTasks: 25,        // tasks no mock (representativas, não exaustivas)
  tasksDone: 12,
  tasksInProgress: 3,
  bugsOpen: 0,           // CORS corrigido no PR #5; sem bugs abertos no momento
  weeklyVelocity: 62,    // tasks concluídas / tasks planejadas no sprint atual (%)
  prsMerged: 5,          // PRs reais mergeados (PR #2, #4, #5 + 2 iniciais)
  coveragePercent: 28,   // cobertura atual — baixa, testes em andamento
  overallProgress: 32,   // ~32%: infra/arq concluída; consulta 64%; demais zeradas
}
