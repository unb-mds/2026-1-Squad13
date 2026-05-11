import { GitPullRequest, GitCommit, CheckCircle2, Clock } from 'lucide-react'
import type { Member } from '@/entities/member'
import { Avatar } from '@/shared/ui/avatar'
import { ProgressBar } from '@/shared/ui/progress-bar'

interface MemberCardProps {
  member: Member
}

export function MemberCard({ member }: MemberCardProps) {
  return (
    <div className="bg-surface-2 border border-border-subtle rounded-xl p-5 space-y-4 hover:border-border-default transition-all animate-fade-in">
      <div className="flex items-center gap-3">
        <Avatar initials={member.avatarInitials} color={member.avatarColor} size="lg" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-white truncate">{member.name}</p>
          <p className="text-xs text-slate-500">{member.role}</p>
        </div>
      </div>

      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">Produtividade</span>
          <span className="font-semibold" style={{ color: member.avatarColor }}>{member.productivity}%</span>
        </div>
        <ProgressBar
          value={member.productivity}
          barClassName="bg-current"
          className="[--tw-text-opacity:1]"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Stat icon={CheckCircle2} label="Tasks" value={`${member.tasksCompleted} done`} color="text-green-400" />
        <Stat icon={Clock} label="Pendentes" value={`${member.tasksPending} tasks`} color="text-yellow-400" />
        <Stat icon={GitPullRequest} label="PRs" value={`${member.prsMerged}/${member.prsOpened}`} color="text-blue-400" />
        <Stat icon={GitCommit} label="Commits" value={member.commits.toString()} color="text-purple-400" />
      </div>

      <div className="border-t border-border-subtle pt-3">
        <p className="text-xs text-slate-500 mb-1">Foco atual</p>
        <p className="text-xs text-slate-300 font-medium">{member.currentFocus}</p>
      </div>
    </div>
  )
}

function Stat({ icon: Icon, label, value, color }: { icon: any; label: string; value: string; color: string }) {
  return (
    <div className="bg-surface-3 rounded-lg p-2.5">
      <div className={`flex items-center gap-1.5 mb-0.5 ${color}`}>
        <Icon className="w-3 h-3" />
        <span className="text-[10px] uppercase tracking-wider font-medium">{label}</span>
      </div>
      <p className="text-sm font-semibold text-white">{value}</p>
    </div>
  )
}
