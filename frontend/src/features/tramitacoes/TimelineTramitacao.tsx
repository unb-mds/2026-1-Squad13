import { AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import type { MovimentacaoTramitacao } from '@/shared/types'
import { formatarData, formatarTempo } from '@/shared/lib/utils'

interface TimelineTramitacaoProps {
  movimentacoes: MovimentacaoTramitacao[]
}

export function TimelineTramitacao({ movimentacoes }: TimelineTramitacaoProps) {
  if (!movimentacoes.length) return (
    <p className="text-ink-400 text-sm py-4">Nenhuma movimentação registrada.</p>
  )

  return (
    <div className="relative space-y-0">
      {movimentacoes.map((mov, i) => {
        const isFirst = i === 0
        const isLast = i === movimentacoes.length - 1

        return (
          <div key={mov.id} className="flex gap-4">
            {/* Timeline line */}
            <div className="flex flex-col items-center shrink-0 w-8">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 shrink-0 z-10 ${
                isFirst
                  ? 'bg-volt-400/20 border-volt-400 text-volt-400'
                  : mov.temAtraso
                  ? 'bg-rose-500/20 border-rose-500/50 text-rose-400'
                  : 'bg-ink-700 border-ink-600 text-ink-400'
              }`}>
                {isFirst ? (
                  <Clock className="w-3.5 h-3.5" />
                ) : mov.temAtraso ? (
                  <AlertTriangle className="w-3.5 h-3.5" />
                ) : (
                  <CheckCircle className="w-3.5 h-3.5" />
                )}
              </div>
              {!isLast && (
                <div className="w-0.5 flex-1 bg-ink-700/50 mt-1 mb-1" />
              )}
            </div>

            {/* Content */}
            <div className={`flex-1 pb-6 ${isLast ? 'pb-0' : ''}`}>
              <div className={`rounded-xl p-4 border transition-colors ${
                isFirst
                  ? 'bg-volt-400/5 border-volt-400/20'
                  : mov.temAtraso
                  ? 'bg-rose-500/5 border-rose-500/20'
                  : 'bg-ink-800/50 border-ink-700/40'
              }`}>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1.5">
                      <span className={`text-xs font-medium font-mono px-2 py-0.5 rounded ${
                        isFirst ? 'bg-volt-400/15 text-volt-300' : 'bg-ink-700 text-ink-300'
                      }`}>
                        {mov.orgao}
                      </span>
                      {mov.temAtraso && (
                        <span className="text-xs bg-rose-500/15 text-rose-400 border border-rose-500/25 px-2 py-0.5 rounded-md font-medium">
                          ⚠ Atraso significativo
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-ink-200 leading-snug">{mov.descricao}</p>
                    {mov.responsavel && (
                      <p className="text-xs text-ink-500 mt-1.5">Por {mov.responsavel}</p>
                    )}
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-xs text-ink-300 font-medium">{formatarData(mov.data)}</p>
                    {mov.diasNaEtapa > 0 && (
                      <p className={`text-xs mt-0.5 ${mov.temAtraso ? 'text-rose-400' : 'text-ink-500'}`}>
                        {formatarTempo(mov.diasNaEtapa)} nesta etapa
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
