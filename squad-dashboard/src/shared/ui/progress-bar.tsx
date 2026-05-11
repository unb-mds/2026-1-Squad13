import { cn } from '@/shared/lib/utils'

interface ProgressBarProps {
  value: number
  className?: string
  barClassName?: string
  showLabel?: boolean
}

export function ProgressBar({ value, className, barClassName, showLabel }: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, value))
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-500', barClassName ?? 'bg-blue-500')}
          style={{ width: `${clamped}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-xs text-slate-400 tabular-nums w-8 text-right">{clamped}%</span>
      )}
    </div>
  )
}
