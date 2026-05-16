import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { EmptyState } from '@/shared/ui/empty-state'
import { TrendingUp, Info, Calendar } from 'lucide-react'

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  const data = payload[0].payload
  return (
    <div className="bg-surface-3 border border-border-subtle rounded-lg px-3 py-2 text-xs shadow-2xl min-w-[180px] backdrop-blur-md bg-opacity-95">
      <div className="flex justify-between items-center mb-2 border-b border-border-subtle pb-1.5">
        <p className="text-slate-200 font-bold">{label}</p>
        {data.isFuture ? (
          <span className="text-[8px] bg-indigo-900/60 text-indigo-300 px-1.5 py-0.5 rounded font-bold border border-indigo-500/30 uppercase tracking-tighter">Horizonte Futuro</span>
        ) : (
          <span className="text-[8px] bg-emerald-900/60 text-emerald-300 px-1.5 py-0.5 rounded font-bold border border-emerald-500/30 uppercase tracking-tighter">Observado</span>
        )}
      </div>
      <div className="space-y-2">
        {!data.isFuture && (
          <>
            <div className="flex justify-between gap-4">
              <span className="text-emerald-400 font-medium">Entregue Total:</span>
              <span className="font-bold text-white text-sm">{data.deliveredTotal}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-blue-400">Entregue R1:</span>
              <span className="font-bold text-white">{data.deliveredR1}</span>
            </div>
          </>
        )}
        <div className="flex justify-between gap-4 border-t border-border-subtle/30 pt-1.5">
          <span className="text-slate-400">Escopo Planejado:</span>
          <span className="font-bold text-slate-200">{data.plannedScope}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-500">Meta R1 (Linear):</span>
          <span className="font-bold text-slate-400">{data.idealR1 !== null ? Math.round(data.idealR1) : '-'}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-500">Meta Final (Linear):</span>
          <span className="font-bold text-slate-400">{Math.round(data.idealTotal)}</span>
        </div>
      </div>
    </div>
  )
}

interface ProjectBurnupChartProps {
  data?: {
    label: string
    plannedScope: number
    deliveredR1: number | null
    deliveredTotal: number | null
    idealR1: number
    idealTotal: number
    isFuture: boolean
  }[]
  metadata?: {
    startDate: string
    release1Date: string
    release2Date: string
    methodology: string
  }
}

export function ProjectBurnupChart({ data, metadata }: ProjectBurnupChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-surface-2 border border-border-subtle rounded-xl p-5 h-[320px] flex flex-col">
        <p className="text-sm font-semibold text-white mb-4">Progresso do Projeto (Burnup)</p>
        <div className="flex-1 flex items-center justify-center">
          <EmptyState
            title="Sem dados de burnup"
            description="Aguardando catalogação de entregáveis."
            icon={TrendingUp}
          />
        </div>
      </div>
    )
  }

  const todayLabel = new Date().toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
  const r1Label = metadata?.release1Date ? new Date(metadata.release1Date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }) : ''
  const r2Label = metadata?.release2Date ? new Date(metadata.release2Date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }) : ''

  return (
    <div className="bg-surface-2 border border-border-subtle rounded-xl p-6 shadow-sm">
      <div className="flex flex-col md:flex-row justify-between items-start gap-4 mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-base font-bold text-white tracking-tight">Evolução por Entregáveis</h3>
            <div className="group relative">
              <Info className="w-3.5 h-3.5 text-slate-500 cursor-help" />
              <div className="absolute left-0 bottom-full mb-2 w-72 p-3 bg-surface-3 border border-border-subtle rounded-lg text-[10px] leading-relaxed text-slate-400 hidden group-hover:block z-50 shadow-2xl">
                <p className="font-bold text-slate-200 mb-1">Metodologia Auditável</p>
                {metadata?.methodology || 'Burnup baseado no Story Map.'}
              </div>
            </div>
          </div>
          <p className="text-xs text-slate-500 font-medium">Contagem de features do Story Map vs Metas de Release</p>
        </div>

        <div className="flex flex-wrap gap-x-6 gap-y-2">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-slate-800 border border-slate-700" />
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Escopo</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]" />
            <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">Entregue</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-slate-500 border-t-2 border-dashed border-slate-600" />
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Ideal</span>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={data} margin={{ top: 20, right: 10, left: -25, bottom: 0 }}>
          <defs>
            <linearGradient id="colorDelivered" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorFuture" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#334155" stopOpacity={0.05} />
              <stop offset="95%" stopColor="#334155" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a35" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fill: '#64748b', fontSize: 10, fontWeight: 500 }}
            axisLine={false}
            tickLine={false}
            interval="preserveStartEnd"
            padding={{ left: 10, right: 10 }}
          />
          <YAxis
            tick={{ fill: '#64748b', fontSize: 10, fontWeight: 600 }}
            axisLine={false}
            tickLine={false}
            domain={[0, 'dataMax + 2']}
          />
          <Tooltip content={<CustomTooltip />} />

          {/* Hoje */}
          <ReferenceLine
            x={todayLabel}
            stroke="#6366f1"
            strokeWidth={1}
            strokeDasharray="3 3"
            label={{ value: 'HOJE', position: 'insideTopLeft', fill: '#818cf8', fontSize: 9, fontWeight: 900, letterSpacing: '0.1em' }}
          />

          {/* Release 1 Milestone (MVP) */}
          <ReferenceLine
            x={r1Label}
            stroke="#f59e0b"
            strokeWidth={2}
            strokeDasharray="5 5"
            label={{ value: 'MVP (R1)', position: 'top', fill: '#fbbf24', fontSize: 10, fontWeight: 800, letterSpacing: '0.05em' }}
          />

          {/* Release 2 Milestone */}
          <ReferenceLine
            x={r2Label}
            stroke="#ef4444"
            strokeWidth={1}
            strokeDasharray="3 3"
            label={{ value: 'MVP (R2)', position: 'top', fill: '#f87171', fontSize: 10, fontWeight: 800 }}
          />

          {/* Área de Escopo (Teto) */}
          <Area
            type="stepAfter"
            dataKey="plannedScope"
            stroke="#334155"
            fill="url(#colorFuture)"
            strokeWidth={1}
            strokeDasharray="4 4"
            activeDot={false}
          />

          {/* Linhas Ideais */}
          <Area
            type="monotone"
            dataKey="idealTotal"
            stroke="#475569"
            fill="transparent"
            strokeWidth={1.5}
            strokeDasharray="3 3"
            activeDot={false}
          />

          <Area
            type="monotone"
            dataKey="idealR1"
            stroke="#64748b"
            fill="transparent"
            strokeWidth={1.5}
            strokeDasharray="3 3"
            activeDot={false}
          />

          {/* Progresso Real - connectNulls false garante que a linha pare no último dado real */}
          <Area
            type="monotone"
            dataKey="deliveredTotal"
            stroke="#10b981"
            strokeWidth={4}
            fillOpacity={1}
            fill="url(#colorDelivered)"
            connectNulls={false}
            dot={(props: any) => {
              const { cx, cy, payload } = props;
              if (payload.isFuture || payload.deliveredTotal === null) return <g />;
              // Destacar apenas o último ponto
              return <circle cx={cx} cy={cy} r={3} fill="#10b981" stroke="#064e3b" strokeWidth={1} />;
            }}
            activeDot={{ r: 6, strokeWidth: 2, fill: '#10b981', stroke: '#fff' }}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Resumo Executivo R1 */}
      <div className="mt-6 pt-6 border-t border-border-subtle/50 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="space-y-1">
          <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Target MVP (R1)</p>
          <p className="text-sm font-bold text-white flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-amber-500" />
            27 Mai 2026
          </p>
        </div>
        <div className="space-y-1">
          <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Escopo R1</p>
          <p className="text-sm font-bold text-white">8 Entregáveis</p>
        </div>
        <div className="space-y-1">
          <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Status Atual</p>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <p className="text-sm font-bold text-emerald-400">Em Ritmo</p>
          </div>
        </div>
        <div className="space-y-1">
          <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Data Snapshot</p>
          <p className="text-sm font-bold text-slate-400">{new Date().toLocaleDateString('pt-BR')}</p>
        </div>
      </div>
    </div>
  )
}
