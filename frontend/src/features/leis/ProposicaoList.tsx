import type { Proposicao } from '@/shared/types'
import { ProposicaoCard } from './ProposicaoCard'

interface ProposicaoListProps {
  proposicoes: Proposicao[]
}

export function ProposicaoList({ proposicoes }: ProposicaoListProps) {
  return (
    <div className="space-y-3">
      {proposicoes.map((p) => (
        <ProposicaoCard key={p.id} proposicao={p} />
      ))}
    </div>
  )
}
