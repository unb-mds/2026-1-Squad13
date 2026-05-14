import { CheckCircle2, Clock, Activity, TrendingUp, AlertTriangle } from 'lucide-react'
import { KpiCard } from '@/widgets/kpi-card'
import { BurndownChart } from '@/widgets/burndown-chart'
import { CommitsChart } from '@/widgets/commits-chart'
import { ProgressBar } from '@/shared/ui/progress-bar'
import { Skeleton } from '@/shared/ui/skeleton'
import { useGithubData } from '@/shared/api/github-data-service'

export function DashboardPage() {
  const { data: gh, loading, error } = useGithubData()
  
  const activeIssues = gh?.issues.open ?? 0
  const closedIssues = gh?.issues.closed ?? 0
  const totalIssues = activeIssues + closedIssues
  
  const overallProgress = gh && totalIssues > 0 
    ? Math.round((closedIssues / totalIssues) * 100) 
    : 0

  const nextMilestone = gh?.milestones.find(m => m.state === 'open')
  const daysRemaining = nextMilestone?.dueOn 
    ? Math.ceil((new Date(nextMilestone.dueOn).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
    : null

  const features = gh?.features || []

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4 text-center">
        <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
          <AlertTriangle className="w-6 h-6 text-red-500" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-white">Falha ao carregar dados</h2>
          <p className="text-sm text-slate-500 max-w-xs mx-auto">
            Não foi possível recuperar as métricas do GitHub. Verifique sua conexão ou se o token expirou.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-xl font-bold text-white">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-0.5">MDS · Squad 13</p>
      </div>

      {/* KPIs Essenciais */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard 
          title="Entregue" 
          value={closedIssues} 
          icon={CheckCircle2} 
          glowColor="green"
          trendLabel={`de ${totalIssues} total`} 
          trend="neutral"
          isLoading={loading}
        />
        <KpiCard 
          title="Em Aberto" 
          value={activeIssues} 
          icon={Activity} 
          glowColor="blue"
          trendLabel="backlog + sprint" 
          trend="neutral" 
          isLoading={loading}
        />
        <KpiCard 
          title="Progresso MVP" 
          value={`${overallProgress}%`} 
          icon={TrendingUp} 
          glowColor="purple"
          trendLabel="Baseado em issues" 
          trend="up" 
          isLoading={loading}
        />
        <KpiCard 
          title="Próxima Entrega" 
          value={daysRemaining !== null ? `${daysRemaining}d` : 'TBD'} 
          icon={Clock} 
          glowColor="yellow"
          trendLabel={nextMilestone?.title || 'Sem milestone'} 
          trend="neutral" 
          isLoading={loading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Lado Esquerdo: Features e Métricas de Fluxo */}
        <div className="space-y-6">
          <div className="bg-surface-2 border border-border-subtle rounded-xl p-5">
            <p className="text-sm font-semibold text-white mb-4">Progresso por Feature</p>
            <div className="space-y-4">
              {loading ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="space-y-2">
                    <Skeleton className="h-3 w-32" />
                    <Skeleton className="h-2 w-full" />
                  </div>
                ))
              ) : features.length > 0 ? (
                features.map(f => (
                  <div key={f.id} className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-300 truncate font-medium">{f.name}</span>
                      <span className="text-xs text-slate-500 tabular-nums ml-2">{f.tasksDone}/{f.tasksTotal} ({f.progress}%)</span>
                    </div>
                    <ProgressBar
                      value={f.progress}
                      barClassName={f.progress >= 100 ? 'bg-green-500' : 'bg-blue-500'}
                    />
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500 text-center py-4">Nenhuma feature mapeada.</p>
              )}
            </div>
          </div>

          {/* Métricas de Fluxo */}
          {!loading && gh && gh.metrics && (
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-surface-3 border border-border-subtle rounded-lg p-3">
                <p className="text-[10px] text-slate-500 uppercase font-bold mb-1">Scope Change</p>
                <p className={`text-sm font-bold ${(gh.metrics.scopeChange || 0) > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {(gh.metrics.scopeChange || 0) > 0 ? '+' : ''}{gh.metrics.scopeChange || 0}%
                </p>
              </div>
              <div className="bg-surface-3 border border-border-subtle rounded-lg p-3">
                <p className="text-[10px] text-slate-500 uppercase font-bold mb-1">Throughput</p>
                <p className="text-sm font-bold text-white">{gh.metrics.throughput || 0} <span className="text-[10px] font-normal text-slate-500">it/dia</span></p>
              </div>
              <div className="bg-surface-3 border border-border-subtle rounded-lg p-3">
                <p className="text-[10px] text-slate-500 uppercase font-bold mb-1">Completion</p>
                <p className="text-sm font-bold text-blue-400">{gh.metrics.completionRate || 0}%</p>
              </div>
            </div>
          )}
        </div>

        {/* Lado Direito: Burndown */}
        <BurndownChart data={gh?.burndownData} />
      </div>

      {/* Gráfico de Commits */}
      <div className="grid grid-cols-1 gap-6">
        <CommitsChart data={gh?.commitsByDay} />
      </div>

      {gh && (
        <p className="text-xs text-slate-600 text-right">
          Sincronizado com GitHub em {new Date(gh.generatedAt).toLocaleString('pt-BR')}
        </p>
      )}
    </div>
  )
}
