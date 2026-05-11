import { Search, X, SlidersHorizontal } from 'lucide-react'
import { Input, Select } from '@/shared/ui'
import { TIPOS_PROPOSICAO, STATUS_PROPOSICAO, ORGAOS } from '@/shared/constants'
import type { FiltrosProposicao } from '@/shared/types'

const FILTROS_VAZIOS: FiltrosProposicao = {
  busca: '',
  orgaoOrigem: '',
  tipo: '',
  status: '',
  dataInicio: '',
  dataFim: '',
}

interface FiltrosProps {
  filtros: FiltrosProposicao
  onChange: (f: FiltrosProposicao) => void
}

export function PainelFiltros({ filtros, onChange }: FiltrosProps) {
  const set = (key: keyof FiltrosProposicao) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    onChange({ ...filtros, [key]: e.target.value })

  const limpar = () => onChange(FILTROS_VAZIOS)
  const temFiltroAtivo = Object.values(filtros).some(Boolean)

  return (
    <div className="bg-ink-800 border border-ink-700/50 rounded-xl p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4 text-ink-400" />
          <span className="text-sm font-medium text-ink-200">Filtros</span>
          {temFiltroAtivo && (
            <span className="bg-volt-400/20 text-volt-300 text-xs px-2 py-0.5 rounded-full border border-volt-400/25">
              ativo
            </span>
          )}
        </div>
        {temFiltroAtivo && (
          <button
            onClick={limpar}
            className="flex items-center gap-1 text-xs text-ink-400 hover:text-rose-400 transition-colors"
          >
            <X className="w-3 h-3" />
            Limpar filtros
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
        <div className="xl:col-span-2">
          <Input
            placeholder="Buscar por ementa, número, autor..."
            value={filtros.busca}
            onChange={set('busca')}
            leftIcon={<Search className="w-4 h-4" />}
          />
        </div>

        <Select value={filtros.orgaoOrigem} onChange={set('orgaoOrigem')}>
          <option value="">Todos os órgãos</option>
          {ORGAOS.map((o) => <option key={o} value={o}>{o}</option>)}
        </Select>

        <Select value={filtros.tipo} onChange={set('tipo')}>
          <option value="">Todos os tipos</option>
          {TIPOS_PROPOSICAO.map((t) => <option key={t} value={t}>{t}</option>)}
        </Select>

        <Select value={filtros.status} onChange={set('status')}>
          <option value="">Todos os status</option>
          {STATUS_PROPOSICAO.map((s) => <option key={s} value={s}>{s}</option>)}
        </Select>

        <div className="flex gap-2">
          <Input
            type="date"
            value={filtros.dataInicio}
            onChange={set('dataInicio')}
            placeholder="De"
          />
          <Input
            type="date"
            value={filtros.dataFim}
            onChange={set('dataFim')}
            placeholder="Até"
          />
        </div>
      </div>
    </div>
  )
}

export { FILTROS_VAZIOS }
