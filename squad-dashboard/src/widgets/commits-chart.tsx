import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { EmptyState } from '@/shared/ui/empty-state'
import { GitCommit } from 'lucide-react'

interface CommitDay {
  date: string
  commits: number
}

interface CommitsChartProps {
  data?: CommitDay[]
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface-3 border border-border-subtle rounded-lg px-3 py-2 text-xs">
      <p className="text-slate-400">{label}: <span className="text-white font-semibold">{payload[0].value} commits</span></p>
    </div>
  )
}

export function CommitsChart({ data }: CommitsChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-surface-2 border border-border-subtle rounded-xl p-5 h-[228px] flex flex-col">
        <p className="text-sm font-semibold text-white mb-4">Commits por Dia</p>
        <div className="flex-1 flex items-center justify-center">
          <EmptyState 
            title="Sem histórico de commits" 
            description="Não foi possível carregar a atividade recente."
            icon={GitCommit}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="bg-surface-2 border border-border-subtle rounded-xl p-5">
      <p className="text-sm font-semibold text-white mb-4">Commits por Dia</p>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} barSize={24}>
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
