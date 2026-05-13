import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { EmptyState } from '@/shared/ui/empty-state'
import { TrendingDown } from 'lucide-react'

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

interface BurndownChartProps {
  data?: { day: string; remaining: number; ideal: number }[]
}

export function BurndownChart({ data }: BurndownChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-surface-2 border border-border-subtle rounded-xl p-5 h-[268px] flex flex-col">
        <p className="text-sm font-semibold text-white mb-4">Burndown do MVP</p>
        <div className="flex-1 flex items-center justify-center">
          <EmptyState 
            title="Sem dados de burndown" 
            description="Cálculo dinâmico aguardando issues."
            icon={TrendingDown}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="bg-surface-2 border border-border-subtle rounded-xl p-5">
      <p className="text-sm font-semibold text-white mb-4">Burndown do MVP</p>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a35" vertical={false} />
          <XAxis dataKey="day" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
          <Line type="monotone" dataKey="ideal" name="Ideal" stroke="#64748b" strokeDasharray="5 5" dot={false} />
          <Line type="monotone" dataKey="remaining" name="Restante" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: '#3b82f6' }} activeDot={{ r: 6 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
