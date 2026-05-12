import { useNavigate } from 'react-router-dom'
import { Clock, AlertTriangle, ChevronRight } from 'lucide-react'
import type { Proposicao } from '@/shared/types'
import { corStatus, corTipo, formatarTempo, formatarDataCurta } from '@/shared/lib/utils'



interface ProposicaoCardProps {
  proposicao: Proposicao
}

export function ProposicaoCard({ proposicao }: ProposicaoCardProps) {
  const navigate = useNavigate()

  return (
    <div
      onClick={() => navigate(`/proposicoes/${proposicao.id}`)}
      className={`group relative bg-ink-800 border rounded-xl p-4 cursor-pointer transition-all duration-200 hover:border-volt-400/30 hover:bg-ink-700/50 hover:shadow-lg hover:shadow-volt-400/5 ${
        proposicao.atrasoCritico ? 'border-rose-500/40 shadow-rose-500/5' : 'border-ink-700/50'
      }`}
    >
      {proposicao.atrasoCritico && (
        <div className="absolute top-3 right-3 flex items-center gap-1.5 px-2 py-0.5 bg-rose-500/10 border border-rose-500/20 rounded-full">
          <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
          <span className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Atraso Crítico</span>
        </div>
      )}

      <div className="flex items-start gap-3 pr-8">
        {/* Tipo badge */}
        <span className={`shrink-0 mt-0.5 inline-flex px-2 py-1 rounded-md text-xs font-display font-600 ${corTipo(proposicao.tipo)}`}>
          {proposicao.tipo}
        </span>

        <div className="flex-1 min-w-0">
          {/* Número e ano */}
          <p className="text-xs text-ink-400 font-mono mb-1">
            {proposicao.numero}/{proposicao.ano}
          </p>

          {/* Ementa */}
          <p className="text-sm text-ink-100 leading-snug line-clamp-2 group-hover:text-white transition-colors">
            {proposicao.ementaResumida}
          </p>

          {/* Meta */}
          <div className="flex flex-wrap items-center gap-2 mt-2.5">
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium border ${corStatus(proposicao.status)}`}>
              {proposicao.status}
            </span>
            <span className="text-xs text-ink-500">·</span>
            <span className="text-xs text-ink-400">{proposicao.orgaoOrigem}</span>
            <span className="text-xs text-ink-500">·</span>
            <span className="text-xs text-ink-400 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatarTempo(proposicao.tempoTotalDias)}
            </span>
            <span className="text-xs text-ink-500">·</span>
            <span className="text-xs text-ink-500">{formatarDataCurta(proposicao.dataApresentacao)}</span>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-1 mt-2">
            {proposicao.tags.slice(0, 3).map((tag) => (
              <span key={tag} className="px-1.5 py-0.5 bg-ink-700/50 text-ink-400 text-xs rounded">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="absolute right-3 bottom-4 opacity-0 group-hover:opacity-100 transition-opacity">
        <ChevronRight className="w-4 h-4 text-volt-400" />
      </div>
    </div>
  )
}

export function ProposicaoListaSkeleton() {
  return (
    <div className="space-y-3">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="bg-ink-800 border border-ink-700/50 rounded-xl p-4 animate-pulse">
          <div className="flex gap-3">
            <div className="w-10 h-6 bg-ink-700 rounded-md" />
            <div className="flex-1 space-y-2">
              <div className="h-3 bg-ink-700 rounded w-20" />
              <div className="h-4 bg-ink-700 rounded w-3/4" />
              <div className="h-3 bg-ink-700 rounded w-1/2" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
