import { useState, useEffect } from 'react'
import { Search, X, SlidersHorizontal, Calendar } from 'lucide-react'
import { Input, Select } from '@/shared/ui'
import { TIPOS_PROPOSICAO, STATUS_PROPOSICAO, ORGAOS } from '@/shared/constants'
import type { FiltrosProposicao } from '@/shared/types'
import { useDebounce } from '@/shared/lib/hooks/use-debounce'

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
  const [localBusca, setLocalBusca] = useState(filtros.busca)
  const debouncedBusca = useDebounce(localBusca, 400)

  // Sincroniza busca debounced com o pai
  useEffect(() => {
    if (debouncedBusca !== filtros.busca) {
      onChange({ ...filtros, busca: debouncedBusca })
    }
  }, [debouncedBusca, filtros, onChange])

  // Sincroniza estado local quando filtros são resetados externamente
  useEffect(() => {
    setLocalBusca(filtros.busca)
  }, [filtros.busca])

  const set = (key: keyof FiltrosProposicao) => (val: string) =>
    onChange({ ...filtros, [key]: val })

  const limpar = () => {
    setLocalBusca('')
    onChange(FILTROS_VAZIOS)
  }
  
  const totalFiltrosAtivos = Object.entries(filtros).filter(([key, val]) => key !== 'busca' && !!val).length + (filtros.busca ? 1 : 0)

  return (
    <div className="bg-ink-800 border border-ink-700/50 rounded-2xl p-5 shadow-xl shadow-black/20">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-volt-400/10 rounded-lg">
            <SlidersHorizontal className="w-4 h-4 text-volt-400" />
          </div>
          <span className="text-sm font-display font-700 text-white uppercase tracking-wider">Filtros Avançados</span>
          {totalFiltrosAtivos > 0 && (
            <span className="bg-volt-400 text-ink-900 text-[10px] font-bold px-2 py-0.5 rounded-full">
              {totalFiltrosAtivos}
            </span>
          )}
        </div>
        {totalFiltrosAtivos > 0 && (
          <button
            onClick={limpar}
            className="flex items-center gap-1.5 text-xs font-medium text-ink-400 hover:text-rose-400 transition-all active:scale-95"
          >
            <X className="w-3.5 h-3.5" />
            Limpar tudo
          </button>
        )}
      </div>

      <div className="space-y-6">
        {/* Busca e Datas */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-7">
            <label className="text-[10px] font-bold text-ink-500 uppercase mb-1.5 block ml-1">Palavra-chave</label>
            <Input
              placeholder="Ementa, número, autor ou tags..."
              value={localBusca}
              onChange={(e) => setLocalBusca(e.target.value)}
              leftIcon={<Search className="w-4 h-4 text-ink-400" />}
              className="bg-ink-900/50 border-ink-700/50 focus:border-volt-400/50 transition-all"
            />
          </div>

          <div className="lg:col-span-5">
            <label className="text-[10px] font-bold text-ink-500 uppercase mb-1.5 block ml-1">Período de Apresentação</label>
            <div className="flex items-center gap-2 bg-ink-900/50 border border-ink-700/50 rounded-xl px-3 py-0.5 focus-within:border-volt-400/50 transition-all">
              <Calendar className="w-4 h-4 text-ink-500 shrink-0" />
              <input
                type="date"
                value={filtros.dataInicio}
                onChange={(e) => set('dataInicio')(e.target.value)}
                className="bg-transparent border-0 text-sm text-ink-200 focus:ring-0 w-full p-2 [color-scheme:dark]"
              />
              <span className="text-ink-600 text-xs font-bold px-1">ATÉ</span>
              <input
                type="date"
                value={filtros.dataFim}
                onChange={(e) => set('dataFim')(e.target.value)}
                className="bg-transparent border-0 text-sm text-ink-200 focus:ring-0 w-full p-2 [color-scheme:dark]"
              />
            </div>
          </div>
        </div>

        {/* Órgão (Chips) */}
        <div>
          <label className="text-[10px] font-bold text-ink-500 uppercase mb-2.5 block ml-1">Órgão de Origem</label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => set('orgaoOrigem')('')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
                !filtros.orgaoOrigem 
                  ? 'bg-volt-400 text-ink-900 border-volt-400 shadow-lg shadow-volt-400/10' 
                  : 'bg-ink-700/30 text-ink-400 border-ink-700/50 hover:border-ink-500'
              }`}
            >
              Todos
            </button>
            {ORGAOS.slice(0, 2).map((o) => (
              <button
                key={o}
                onClick={() => set('orgaoOrigem')(o)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
                  filtros.orgaoOrigem === o 
                    ? 'bg-volt-400 text-ink-900 border-volt-400 shadow-lg shadow-volt-400/10' 
                    : 'bg-ink-700/30 text-ink-400 border-ink-700/50 hover:border-ink-500'
                }`}
              >
                {o}
              </button>
            ))}
          </div>
        </div>

        {/* Tipo e Status */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-[10px] font-bold text-ink-500 uppercase mb-1.5 block ml-1">Tipo de Proposição</label>
            <Select 
              value={filtros.tipo} 
              onChange={(e) => set('tipo')(e.target.value)}
              className="bg-ink-900/50 border-ink-700/50"
            >
              <option value="">Qualquer tipo</option>
              {TIPOS_PROPOSICAO.map((t) => <option key={t} value={t}>{t}</option>)}
            </Select>
          </div>

          <div>
            <label className="text-[10px] font-bold text-ink-500 uppercase mb-1.5 block ml-1">Situação / Status</label>
            <Select 
              value={filtros.status} 
              onChange={(e) => set('status')(e.target.value)}
              className="bg-ink-900/50 border-ink-700/50"
            >
              <option value="">Qualquer situação</option>
              {STATUS_PROPOSICAO.map((s) => <option key={s} value={s}>{s}</option>)}
            </Select>
          </div>
        </div>
      </div>
    </div>
  )
}

export { FILTROS_VAZIOS }
