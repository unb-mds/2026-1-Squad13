import type { LucideIcon } from 'lucide-react'
import { Search } from 'lucide-react'

interface EmptyStateProps {
  title: string
  description?: string
  icon?: LucideIcon
}

export function EmptyState({ title, description, icon: Icon = Search }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center w-full">
      <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-4">
        <Icon className="w-5 h-5 text-slate-500" />
      </div>
      <p className="text-slate-300 font-medium">{title}</p>
      {description && <p className="text-slate-500 text-sm mt-1">{description}</p>}
    </div>
  )
}
