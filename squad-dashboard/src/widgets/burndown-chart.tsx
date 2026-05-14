import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { EmptyState } from '@/shared/ui/empty-state'
import { TrendingDown } from 'lucide-react'

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  const data = payload[0].payload
  return (
    <div className="bg-surface-3 border border-border-subtle rounded-lg px-3 py-2 text-xs shadow-xl">
      <p className="text-slate-400 mb-2 font-medium border-b border-border-subtle pb-1">{label}</p>
      <div className="space-y-1">
        <p className="flex justify-between gap-4">
          <span className="text-blue-400">Restante:</span>
          <span className="font-bold text-white">{data.remaining}</span>
        </p>
        <p className="flex justify-between gap-4 border-b border-border-subtle pb-1 mb-1">
          <span className="text-slate-500">Ideal:</span>
          <span className="font-bold text-slate-400">{data.ideal}</span>
        </p>
        <p className="flex justify-between gap-4">
          <span className="text-indigo-400">Escopo Total:</span>
          <span className="font-bold text-white">{data.scope}</span>
        </p>
        {(data.addedItems > 0 || data.completedItems > 0) && (
          <div className="mt-2 pt-1 border-t border-border-subtle/50 text-[10px]">
            {data.addedItems > 0 && (
              <p className="text-amber-400">+ {data.addedItems} novo(s)</p>
            )}
            {data.completedItems > 0 && (
              <p className="text-emerald-400">✓ {data.completedItems} concluído(s)</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

interface BurndownChartProps {
  data?: { 
    label: string
    remaining: number
    ideal: number
    scope: number
    addedItems: number
    completedItems: number
  }[]
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
      <div className="flex justify-between items-center mb-6">
        <div>
          <p className="text-sm font-semibold text-white">Burndown do MVP</p>
          <p className="text-[10px] text-slate-500 uppercase tracking-wider">Itens Restantes vs Ideal</p>
        </div>
        <div className="flex gap-4 text-[10px]">
           <div className="flex items-center gap-1.5">
             <div className="w-2 h-2 rounded-full bg-indigo-500/50" />
             <span className="text-slate-400">Escopo</span>
           </div>
           <div className="flex items-center gap-1.5">
             <div className="w-2 h-2 rounded-full bg-blue-500" />
             <span className="text-slate-400">Real</span>
           </div>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a35" vertical={false} />
          <XAxis 
            dataKey="label" 
            tick={{ fill: '#64748b', fontSize: 10 }} 
            axisLine={false} 
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis 
            tick={{ fill: '#64748b', fontSize: 10 }} 
            axisLine={false} 
            tickLine={false} 
          />
          <Tooltip content={<CustomTooltip />} />
          
          {/* Área de Escopo (Fundo) */}
          <Line 
            type="stepAfter" 
            dataKey="scope" 
            stroke="#6366f1" 
            strokeWidth={1} 
            strokeOpacity={0.3}
            dot={false}
            activeDot={false}
          />
          
          <Line 
            type="monotone" 
            dataKey="ideal" 
            stroke="#475569" 
            strokeWidth={1}
            strokeDasharray="4 4" 
            dot={false} 
          />
          
          <Line 
            type="monotone" 
            dataKey="remaining" 
            stroke="#3b82f6" 
            strokeWidth={2.5} 
            dot={{ r: 3, fill: '#3b82f6', strokeWidth: 0 }} 
            activeDot={{ r: 5, strokeWidth: 0 }} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
