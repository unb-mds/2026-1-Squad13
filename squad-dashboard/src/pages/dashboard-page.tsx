import { CheckCircle2, Clock, Bug, Zap, GitPullRequest, Shield, TrendingUp, Activity, AlertTriangle } from 'lucide-react'
import { KpiCard } from '@/widgets/kpi-card'
import { WeeklyChart } from '@/widgets/weekly-chart'
import { BurndownChart } from '@/widgets/burndown-chart'
import { CommitsChart } from '@/widgets/commits-chart'
import { ProductivityChart } from '@/widgets/productivity-chart'
import { ProgressBar } from '@/shared/ui/progress-bar'
import { Skeleton } from '@/shared/ui/skeleton'
import { useGithubData } from '@/shared/api/github-data-service'

export function DashboardPage() {
  const { data: gh, loading, error } = useGithubData()
  
  const features = gh?.features || []
  const prsMerged = gh?.pullRequests.merged ?? 0
  const tasksDone = gh?.issues.closed ?? 0
  const totalTasks = gh ? (gh.issues.open + gh.issues.closed) : 0
  const tasksInProgress = gh ? gh.tasks.filter(t => t.status === 'in_progress').length : 0
  const bugsOpen = gh ? gh.tasks.filter(t => t.labels.includes('bug') && t.status !== 'done').length : 0
  
  const overallProgress = gh && features.length > 0 
    ? Math.round(features.reduce((acc, f) => acc + f.progress, 0) / features.length) 
    : 0

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
        <p className="text-sm text-slate-500 mt-0.5">Monitoramento de Tramitação de Leis · Squad 13</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard 
          title="Tasks Concluídas" 
          value={tasksDone} 
          icon={CheckCircle2} 
          glowColor="green"
          trendLabel={gh ? `de ${totalTasks} total` : 'N/A'} 
          trend="neutral"
          isLoading={loading}
        />
        <KpiCard 
          title="Em Progresso" 
          value={tasksInProgress} 
          icon={Activity} 
          glowColor="blue"
          trendLabel={gh ? 'tasks ativas' : 'N/A'} 
          trend="neutral" 
          isLoading={loading}
        />
        <KpiCard 
          title="Bugs Abertos" 
          value={bugsOpen} 
          icon={Bug} 
          glowColor="red"
          trendLabel={gh ? 'requer atenção' : 'N/A'} 
          trend="down" 
          isLoading={loading}
        />
        <KpiCard 
          title="Velocidade" 
          value={gh ? 'TBD' : 'N/A'} 
          icon={Zap} 
          glowColor="yellow"
          trendLabel="Aguardando cálculo real" 
          trend="neutral" 
          isLoading={loading}
        />
        <KpiCard 
          title="PRs Mergeados" 
          value={prsMerged} 
          icon={GitPullRequest} 
          glowColor="purple"
          trendLabel={gh ? 'GitHub ao vivo' : 'N/A'} 
          trend="neutral" 
          isLoading={loading}
        />
        <KpiCard 
          title="Cobertura" 
          value={gh ? `${gh.coveragePercent}%` : 'TBD'} 
          icon={Shield} 
          glowColor="green"
          trendLabel={gh ? 'Métrica real CI' : 'Aguardando integração'} 
          trend="neutral" 
          isLoading={loading}
        />
        <KpiCard 
          title="Progresso Geral" 
          value={`${overallProgress}%`} 
          icon={TrendingUp} 
          glowColor="blue"
          trendLabel="Média de features" 
          trend="up" 
          isLoading={loading}
        />
        <KpiCard 
          title="Tarefas Pendentes" 
          value={gh ? (totalTasks - tasksDone) : 0} 
          icon={Clock} 
          glowColor="yellow"
          trendLabel="backlog + ativas" 
          trend="neutral" 
          isLoading={loading}
        />
      </div>

      {/* Feature progress strip */}
      <div className="bg-surface-2 border border-border-subtle rounded-xl p-5">
        <p className="text-sm font-semibold text-white mb-4">Progresso por Feature</p>
        <div className="space-y-3">
          {loading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-3 w-32" />
                <Skeleton className="h-2 w-full" />
              </div>
            ))
          ) : features.length > 0 ? (
            features.map(f => (
              <div key={f.id} className="grid grid-cols-[1fr_auto] gap-4 items-center">
                <div className="space-y-1.5 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-300 truncate font-medium">{f.name}</span>
                    <span className="text-xs text-slate-500 tabular-nums ml-2">{f.progress}%</span>
                  </div>
                  <ProgressBar
                    value={f.progress}
                    barClassName={f.status === 'blocked' ? 'bg-red-500' : f.progress >= 80 ? 'bg-green-500' : 'bg-blue-500'}
                  />
                </div>
                <span className="text-xs text-slate-500 tabular-nums whitespace-nowrap">
                  {f.tasksDone}/{f.tasksTotal}
                </span>
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-500 text-center py-4">Nenhuma feature mapeada via labels.</p>
          )}
        </div>
      </div>
...

      {/* Charts grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <WeeklyChart data={gh?.weeklyCommits?.map(w => ({ week: w.week, completed: 0, added: 0 }))} />
        <BurndownChart data={gh?.burndownData} />
        <CommitsChart data={gh?.commitsByDay} />
        <ProductivityChart data={gh?.contributors?.map(c => ({ name: c.login, score: c.commits }))} />
      </div>

      {gh && (
        <p className="text-xs text-slate-600 text-right">
          Dados do GitHub atualizados em {new Date(gh.generatedAt).toLocaleString('pt-BR')}
        </p>
      )}
    </div>
  )
}
