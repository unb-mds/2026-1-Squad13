import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { mockCommitsByDay } from '@/mocks/metrics'

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface-3 border border-border-subtle rounded-lg px-3 py-2 text-xs">
      <p className="text-slate-400">{label}: <span className="text-white font-semibold">{payload[0].value} commits</span></p>
    </div>
  )
}

export function CommitsChart() {
  return (
    <div className="bg-surface-2 border border-border-subtle rounded-xl p-5">
      <p className="text-sm font-semibold text-white mb-4">Commits por Dia</p>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={mockCommitsByDay} barSize={24}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a35" vertical={false} />
          <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
          <Bar dataKey="commits" fill="#3b82f6" radius={[4, 4, 0, 0]} fillOpacity={0.8} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
