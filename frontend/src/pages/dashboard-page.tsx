import { LayoutDashboard } from 'lucide-react'
import { DashboardMetricas, DashboardGraficos, DashboardResumoStatus } from '@/features/dashboard/DashboardComponents'

export function DashboardPage() {
  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <LayoutDashboard className="w-5 h-5 text-volt-400" />
            <h1 className="font-display font-700 text-2xl text-white">Dashboard</h1>
          </div>
          <p className="text-sm text-ink-400">Visão geral do monitoramento legislativo</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-ink-500 font-mono">
            Última atualização: {new Date().toLocaleDateString('pt-BR')}
          </p>
        </div>
      </div>

      {/* KPIs */}
      <DashboardMetricas />

      {/* Status summary */}
      <DashboardResumoStatus />

      {/* Gráficos */}
      <DashboardGraficos />
    </div>
  )
}
