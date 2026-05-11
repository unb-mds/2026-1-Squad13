import { useState } from 'react'
import type { FeatureStatus } from '@/entities/feature'
import { FeatureCard } from '@/features/features-tracker/feature-card'
import { mockFeatures } from '@/mocks/features'
import { FEATURE_STATUS_CONFIG } from '@/shared/lib/utils'
import { EmptyState } from '@/shared/ui/empty-state'

const ALL_STATUSES: (FeatureStatus | 'all')[] = ['all', 'in_progress', 'review', 'done', 'planned', 'blocked']

export function FeaturesPage() {
  const [filter, setFilter] = useState<FeatureStatus | 'all'>('all')

  const filtered = filter === 'all' ? mockFeatures : mockFeatures.filter(f => f.status === filter)

  return (
    <div className="space-y-5 animate-fade-in">
      <div>
        <h1 className="text-xl font-bold text-white">Features</h1>
        <p className="text-sm text-slate-500 mt-0.5">Funcionalidades do Monitoramento de Tramitação de Leis</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {ALL_STATUSES.map(s => {
          const cfg = s === 'all' ? null : FEATURE_STATUS_CONFIG[s]
          const active = filter === s
          return (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all border ${
                active
                  ? 'bg-blue-500/20 text-blue-400 border-blue-500/40'
                  : 'text-slate-400 border-border-subtle hover:text-slate-200 hover:bg-white/5'
              }`}
            >
              {s === 'all' ? 'Todas' : cfg?.label}
            </button>
          )
        })}
      </div>

      {filtered.length === 0 ? (
        <EmptyState title="Nenhuma feature encontrada" description="Tente outro filtro." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map(f => <FeatureCard key={f.id} feature={f} />)}
        </div>
      )}
    </div>
  )
}
