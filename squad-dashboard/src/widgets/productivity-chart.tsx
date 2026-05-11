import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from 'recharts'
import { mockTeam } from '@/mocks/team'

export function ProductivityChart() {
  const data = mockTeam.map(m => ({
    member: m.name.split(' ')[0],
    produtividade: m.productivity,
  }))

  return (
    <div className="bg-surface-2 border border-border-subtle rounded-xl p-5">
      <p className="text-sm font-semibold text-white mb-2">Produtividade por Membro</p>
      <ResponsiveContainer width="100%" height={220}>
        <RadarChart data={data}>
          <PolarGrid stroke="#2a2a35" />
          <PolarAngleAxis dataKey="member" tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <Radar name="Produtividade" dataKey="produtividade" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.2} strokeWidth={2} />
          <Tooltip
            contentStyle={{ background: '#18181f', border: '1px solid #2a2a35', borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: '#94a3b8' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
