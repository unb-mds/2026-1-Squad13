import { Brain, Info } from 'lucide-react'
import { DISCLAIMER_IA } from '@/shared/constants'
import { formatarTempo } from '@/shared/lib/utils'

interface CardPrevisaoIAProps {
  temPrevisao: boolean
  diasEstimados?: number
  status: string
}

export function CardPrevisaoIA({ temPrevisao, diasEstimados, status }: CardPrevisaoIAProps) {
  const encerrada = ['Aprovada', 'Rejeitada', 'Arquivada', 'Vetada', 'Sancionada'].includes(status)

  if (encerrada) return null

  return (
    <div className={`rounded-xl border p-5 ${
      temPrevisao
        ? 'bg-gradient-to-br from-indigo-500/10 to-violet-500/10 border-indigo-500/25'
        : 'bg-ink-800 border-ink-700/50'
    }`}>
      <div className="flex items-center gap-2 mb-3">
        <div className={`p-1.5 rounded-lg ${temPrevisao ? 'bg-indigo-500/20' : 'bg-ink-700'}`}>
          <Brain className={`w-4 h-4 ${temPrevisao ? 'text-indigo-400' : 'text-ink-400'}`} />
        </div>
        <p className="text-sm font-medium text-white">Estimativa Preditiva</p>
        <span className="text-xs bg-indigo-500/15 text-indigo-400 border border-indigo-500/25 px-1.5 py-0.5 rounded font-medium">
          IA
        </span>
      </div>

      {temPrevisao && diasEstimados ? (
        <>
          <p className="text-xs text-ink-400 mb-2">Tempo estimado até aprovação:</p>
          <p className="text-2xl font-display font-700 text-indigo-300 mb-1">
            ~{formatarTempo(diasEstimados)}
          </p>
          <p className="text-xs text-indigo-400/70 mb-4">
            com base em proposições similares aprovadas
          </p>
          <div className="flex items-start gap-2 p-3 bg-ink-800/60 rounded-lg border border-ink-700/30">
            <Info className="w-3.5 h-3.5 text-ink-500 shrink-0 mt-0.5" />
            <p className="text-xs text-ink-500 leading-relaxed">{DISCLAIMER_IA}</p>
          </div>
        </>
      ) : (
        <p className="text-sm text-ink-400 leading-relaxed">
          Não há dados suficientes para gerar uma previsão confiável para esta proposição.
        </p>
      )}
    </div>
  )
}
