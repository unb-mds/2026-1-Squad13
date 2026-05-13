import type { LucideIcon } from 'lucide-react'
import { cn } from '@/shared/lib/utils'
import { Skeleton } from '@/shared/ui/skeleton'

interface KpiCardProps {
  title: string
  value?: string | number
  subtitle?: string
  icon: LucideIcon
  trend?: 'up' | 'down' | 'neutral'
  trendLabel?: string
  glowColor?: 'blue' | 'purple' | 'green' | 'yellow' | 'red'
  isLoading?: boolean
}

const glowMap = {
  blue: 'shadow-glow border-blue-500/20',
  purple: 'shadow-glow-purple border-purple-500/20',
  green: 'shadow-glow-green border-green-500/20',
  yellow: 'border-yellow-500/20',
  red: 'border-red-500/20',
}

const iconBgMap = {
  blue: 'bg-blue-500/15 text-blue-400',
  purple: 'bg-purple-500/15 text-purple-400',
  green: 'bg-green-500/15 text-green-400',
  yellow: 'bg-yellow-500/15 text-yellow-400',
  red: 'bg-red-500/15 text-red-400',
}

export function KpiCard({ title, value, subtitle, icon: Icon, trend, trendLabel, glowColor = 'blue', isLoading }: KpiCardProps) {
  return (
    <div className={cn(
      'bg-surface-2 border rounded-xl p-5 animate-fade-in transition-all hover:border-opacity-50',
      glowMap[glowColor]
    )}>
      <div className="flex items-start justify-between mb-3">
        <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</p>
        <div className={cn('w-8 h-8 rounded-lg flex items-center justify-center', iconBgMap[glowColor])}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      
      {isLoading ? (
        <div className="space-y-2">
          <Skeleton className="h-8 w-16" />
          <Skeleton className="h-3 w-24" />
        </div>
      ) : (
        <>
          <p className="text-2xl font-bold text-white tabular-nums">{value}</p>
          {(subtitle || trendLabel) && (
            <p className={cn(
              'text-xs mt-1.5',
              trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400' : 'text-slate-500'
            )}>
              {trendLabel ?? subtitle}
            </p>
          )}
        </>
      )}
    </div>
  )
}
