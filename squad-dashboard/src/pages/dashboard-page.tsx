import { CheckCircle2, Clock, Bug, Zap, GitPullRequest, Shield, TrendingUp, Activity } from 'lucide-react'
import { KpiCard } from '@/widgets/kpi-card'
import { WeeklyChart } from '@/widgets/weekly-chart'
import { BurndownChart } from '@/widgets/burndown-chart'
import { CommitsChart } from '@/widgets/commits-chart'
import { ProductivityChart } from '@/widgets/productivity-chart'
import { mockKpis } from '@/mocks/metrics'
import { ProgressBar } from '@/shared/ui/progress-bar'
import { mockFeatures } from '@/mocks/features'
import { useGithubData } from '@/shared/api/github-data-service'

export function DashboardPage() {
  const { data: gh } = useGithubData()
  const features = gh?.features && gh.features.length > 0 ? gh.features : mockFeatures
  
  const prsMerged = gh?.pullRequests.merged ?? mockKpis.prsMerged
  const tasksDone = gh?.issues.closed ?? mockKpis.tasksDone
  const totalTasks = gh ? (gh.issues.open + gh.issues.closed) : mockKpis.totalTasks
  const tasksInProgress = gh ? gh.tasks.filter(t => t.status === 'in_progress').length : mockKpis.tasksInProgress
  const bugsOpen = gh ? gh.tasks.filter(t => t.labels.includes('bug') && t.status !== 'done').length : mockKpis.bugsOpen
  
  // Overall progress is the average of features
  const overallProgress = gh ? Math.round(features.reduce((acc, f) => acc + f.progress, 0) / features.length) : mockKpis.overallProgress

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-xl font-bold text-white">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-0.5">Monitoramento de Tramitação de Leis · Squad 13</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard title="Tasks Concluídas" value={tasksDone} icon={CheckCircle2} glowColor="green"
          trendLabel={`de ${totalTasks} total`} trend="neutral" />
        <KpiCard title="Em Progresso" value={tasksInProgress} icon={Activity} glowColor="blue"
          trendLabel="tasks ativas" trend="neutral" />
        <KpiCard title="Bugs Abertos" value={bugsOpen} icon={Bug} glowColor="red"
          trendLabel="requer atenção" trend="down" />
        <KpiCard title="Velocity" value={`${mockKpis.weeklyVelocity}%`} icon={Zap} glowColor="yellow"
          trendLabel="+3% vs semana ant." trend="up" />
        <KpiCard title="PRs Mergeados" value={prsMerged} icon={GitPullRequest} glowColor="purple"
          trendLabel={gh ? 'GitHub ao vivo' : 'desde o início'} trend="neutral" />
        <KpiCard title="Cobertura" value={`${mockKpis.coveragePercent}%`} icon={Shield} glowColor="green"
          trendLabel="meta: 70%" trend="up" />
        <KpiCard title="Progresso Geral" value={`${overallProgress}%`} icon={TrendingUp} glowColor="blue"
          trendLabel="MVP em 23/mai" trend="up" />
        <KpiCard title="Tarefas Pendentes" value={totalTasks - tasksDone} icon={Clock} glowColor="yellow"
          trendLabel="backlog + ativas" trend="neutral" />
      </div>

      {/* Feature progress strip */}
      <div className="bg-surface-2 border border-border-subtle rounded-xl p-5">
        <p className="text-sm font-semibold text-white mb-4">Progresso por Feature</p>
        <div className="space-y-3">
          {features.map(f => (
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
          ))}
        </div>
      </div>

      {/* Charts grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <WeeklyChart />
        <BurndownChart />
        <CommitsChart data={gh?.commitsByDay} />
        <ProductivityChart />
      </div>

      {gh && (
        <p className="text-xs text-slate-600 text-right">
          Dados do GitHub atualizados em {new Date(gh.generatedAt).toLocaleString('pt-BR')}
        </p>
      )}
    </div>
  )
}
