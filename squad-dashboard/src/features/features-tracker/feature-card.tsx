import { AlertTriangle, CheckCircle2 } from 'lucide-react'
import type { Feature } from '@/entities/feature'
import { Badge } from '@/shared/ui/badge'
import { ProgressBar } from '@/shared/ui/progress-bar'
import { FEATURE_STATUS_CONFIG, formatDate } from '@/shared/lib/utils'
import { mockTeam } from '@/mocks/team'
import { Avatar } from '@/shared/ui/avatar'

interface FeatureCardProps {
  feature: Feature
}

export function FeatureCard({ feature }: FeatureCardProps) {
  const statusCfg = FEATURE_STATUS_CONFIG[feature.status]
  const owner = mockTeam.find(m => m.id === feature.ownerId)

  return (
    <div className="bg-surface-2 border border-border-subtle rounded-xl p-5 space-y-4 hover:border-border-default transition-all animate-fade-in">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-sm font-semibold text-white">{feature.name}</h3>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">{feature.description}</p>
        </div>
        <Badge className={`${statusCfg.bg} ${statusCfg.text} shrink-0`}>{statusCfg.label}</Badge>
      </div>

      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">Progresso</span>
          <span className="text-white font-semibold">{feature.progress}%</span>
        </div>
        <ProgressBar
          value={feature.progress}
          barClassName={feature.status === 'blocked' ? 'bg-red-500' : feature.progress >= 80 ? 'bg-green-500' : 'bg-blue-500'}
        />
      </div>

      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>
          <span className="text-green-400 font-medium">{feature.tasksDone}</span>
          <span className="mx-1">/</span>
          <span>{feature.tasksTotal} tasks</span>
        </span>
        <span>até {formatDate(feature.targetDate)}</span>
      </div>

      {feature.blockers.length > 0 && (
        <div className="space-y-1.5">
          {feature.blockers.map(b => (
            <div key={b} className="flex items-start gap-1.5 text-xs text-orange-400">
              <AlertTriangle className="w-3 h-3 mt-0.5 shrink-0" />
              <span>{b}</span>
            </div>
          ))}
        </div>
      )}

      {feature.blockers.length === 0 && feature.status !== 'planned' && (
        <div className="flex items-center gap-1.5 text-xs text-green-400">
          <CheckCircle2 className="w-3 h-3" />
          <span>Sem blockers</span>
        </div>
      )}

      {owner && (
        <div className="flex items-center gap-2 pt-1 border-t border-border-subtle">
          <Avatar initials={owner.avatarInitials} color={owner.avatarColor} size="sm" />
          <span className="text-xs text-slate-400">{owner.name}</span>
        </div>
      )}
    </div>
  )
}
