import { Search } from 'lucide-react'

interface EmptyStateProps {
  title: string
  description?: string
}

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-4">
        <Search className="w-5 h-5 text-slate-500" />
      </div>
      <p className="text-slate-300 font-medium">{title}</p>
      {description && <p className="text-slate-500 text-sm mt-1">{description}</p>}
    </div>
  )
}
