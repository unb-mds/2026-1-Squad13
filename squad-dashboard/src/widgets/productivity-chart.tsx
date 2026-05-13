import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { EmptyState } from '@/shared/ui/empty-state'
import { Users } from 'lucide-react'

interface ProductivityChartProps {
  data?: { name: string; score: number }[]
}

export function ProductivityChart({ data }: ProductivityChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-surface-2 border border-border-subtle rounded-xl p-5 h-[268px] flex flex-col">
        <p className="text-sm font-semibold text-white mb-4">Produtividade do Time</p>
        <div className="flex-1 flex items-center justify-center">
          <EmptyState 
            title="Sem dados de produtividade" 
            description="Aguardando métricas de contribuição."
            icon={Users}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="bg-surface-2 border border-border-subtle rounded-xl p-5">
      <p className="text-sm font-semibold text-white mb-4">Produtividade do Time</p>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a35" horizontal={false} />
          <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip 
            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
            contentStyle={{ backgroundColor: '#1e1e2d', borderColor: '#2a2a35', borderRadius: '8px', fontSize: '12px' }}
          />
          <Bar dataKey="score" radius={[4, 4, 0, 0]}>
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#3b82f6' : '#8b5cf6'} fillOpacity={0.8} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
