import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { mockBurndown } from '@/mocks/metrics'

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

export function BurndownChart() {
  return (
    <div className="bg-surface-2 border border-border-subtle rounded-xl p-5">
      <p className="text-sm font-semibold text-white mb-4">Burndown — Sprint 3</p>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={mockBurndown}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a35" />
          <XAxis dataKey="day" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
          <Line type="monotone" dataKey="remaining" name="Restante" stroke="#ef4444" strokeWidth={2} dot={{ fill: '#ef4444', r: 3 }} />
          <Line type="monotone" dataKey="ideal" name="Ideal" stroke="#3b82f6" strokeWidth={2} strokeDasharray="4 4" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
