import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { EmptyState } from '@/shared/ui/empty-state'
import { Activity } from 'lucide-react'

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface-3 border border-border-subtle rounded-lg px-3 py-2 text-xs">
      <p className="text-slate-400 mb-1">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }}>{p.name}: <span className="font-semibold">{p.value}</span></p>
      ))}
    </div>
  )
}

interface WeeklyChartProps {
  data?: { week: string; completed: number; added: number }[]
}

export function WeeklyChart({ data }: WeeklyChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-surface-2 border border-border-subtle rounded-xl p-5 h-[268px] flex flex-col">
        <p className="text-sm font-semibold text-white mb-4">Evolução Semanal</p>
        <div className="flex-1 flex items-center justify-center">
          <EmptyState 
            title="Sem dados semanais" 
            description="Métricas de velocidade não encontradas."
            icon={Activity}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="bg-surface-2 border border-border-subtle rounded-xl p-5">
      <p className="text-sm font-semibold text-white mb-4">Evolução Semanal</p>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="gradCompleted" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gradAdded" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a35" />
          <XAxis dataKey="week" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
          <Area type="monotone" dataKey="completed" name="Concluídas" stroke="#3b82f6" fill="url(#gradCompleted)" strokeWidth={2} dot={false} />
          <Area type="monotone" dataKey="added" name="Adicionadas" stroke="#8b5cf6" fill="url(#gradAdded)" strokeWidth={2} dot={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
