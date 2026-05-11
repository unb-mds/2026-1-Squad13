import type { SprintItem, Milestone } from '@/entities/sprint'

export const mockSprints: SprintItem[] = [
  {
    id: 's1',
    title: 'Sprint 1 — Setup, Arquitetura e Base',
    status: 'completed',
    startDate: '2026-04-01',
    endDate: '2026-04-25',
    tasksTotal: 10,
    tasksDone: 10,
    features: ['Layered Architecture', 'CI/CD Inicial', 'Docker Compose', 'ADR-001'],
  },
  {
    id: 's2',
    title: 'Sprint 2 — Consulta e Detalhamento',
    status: 'active',
    startDate: '2026-05-01',
    endDate: '2026-05-23',
    tasksTotal: 10,
    tasksDone: 4,
    features: ['GET /proposicoes', 'Adapters Mock', 'Integração Frontend', 'GET /proposicoes/{id}'],
  },
  {
    id: 's3',
    title: 'Sprint 3 — Dashboard Analítico e Auth',
    status: 'upcoming',
    startDate: '2026-06-02',
    endDate: '2026-06-27',
    tasksTotal: 12,
    tasksDone: 0,
    features: ['Dashboard Analítico', 'Autenticação JWT', 'Proteção de Rotas', 'Métricas Backend'],
  },
  {
    id: 's4',
    title: 'Sprint 4 — Predições e Integrações Reais',
    status: 'upcoming',
    startDate: '2026-07-07',
    endDate: '2026-08-01',
    tasksTotal: 14,
    tasksDone: 0,
    features: ['Adapter Real Câmara', 'Modelo Preditivo', 'Score de Confiança', 'Disclaimer ML'],
  },
]

export const mockMilestones: Milestone[] = [
  {
    id: 'ml1',
    title: 'MVP — Consulta Funcional',
    date: '2026-05-23',
    status: 'active',
    description: 'Consulta de proposições integrada ao backend, com filtros, paginação e detalhamento inicial.',
  },
  {
    id: 'ml2',
    title: 'Beta — Dashboard + Auth',
    date: '2026-06-27',
    status: 'upcoming',
    description: 'Dashboard analítico com KPIs reais, autenticação completa e testes com cobertura mínima de 70%.',
  },
  {
    id: 'ml3',
    title: 'Release v1.0 — Sistema Completo',
    date: '2026-08-08',
    status: 'upcoming',
    description: 'Integração real com APIs da Câmara e Senado, predições com disclaimer e sistema em produção.',
  },
]
