import { cn } from '@/shared/lib/utils'

export function Skeleton({ className }: { className?: string }) {
  return (
    <div className={cn('animate-pulse bg-white/5 rounded-lg', className)} />
  )
}

export function KpiSkeleton() {
  return (
    <div className="bg-surface-2 border border-border-subtle rounded-xl p-5 space-y-3">
      <Skeleton className="h-3 w-24" />
      <Skeleton className="h-8 w-16" />
      <Skeleton className="h-2 w-32" />
    </div>
  )
}
