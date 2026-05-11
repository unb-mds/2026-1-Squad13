import { useState, useEffect, useCallback } from 'react'
import { FileText, AlertCircle } from 'lucide-react'
import { listarProposicoes } from '@/shared/lib/api'
import type { Proposicao, FiltrosProposicao } from '@/shared/types'
import { ITENS_POR_PAGINA } from '@/shared/constants'
import { ProposicaoCard, ProposicaoListaSkeleton } from '@/features/proposicoes/ProposicaoCard'
import { PainelFiltros, FILTROS_VAZIOS } from '@/features/filtros/PainelFiltros'
import { Pagination, EmptyState } from '@/shared/ui'

export function ConsultaProposicoesPage() {
  const [proposicoes, setProposicoes] = useState<Proposicao[]>([])
  const [total, setTotal] = useState(0)
  const [pagina, setPagina] = useState(1)
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState<string | null>(null)
  const [filtros, setFiltros] = useState<FiltrosProposicao>(FILTROS_VAZIOS)

  const buscar = useCallback(async (f: FiltrosProposicao, p: number) => {
    setLoading(true)
    setErro(null)
    try {
      const { items, total } = await listarProposicoes(f, p, ITENS_POR_PAGINA)
      setProposicoes(items)
      setTotal(total)
    } catch (e) {
      setErro(e instanceof Error ? e.message : 'Erro ao carregar proposições.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    buscar(filtros, pagina)
  }, [filtros, pagina, buscar])

  const handleFiltros = (f: FiltrosProposicao) => {
    setFiltros(f)
    setPagina(1)
  }

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-2">
        <FileText className="w-5 h-5 text-volt-400" />
        <h1 className="font-display font-700 text-2xl text-white">Proposições</h1>
        <span className="ml-auto text-xs text-ink-500 font-mono">{total} resultado{total !== 1 ? 's' : ''}</span>
      </div>

      {/* Filtros */}
      <PainelFiltros filtros={filtros} onChange={handleFiltros} />

      {/* Resultados */}
      {loading ? (
        <ProposicaoListaSkeleton />
      ) : erro ? (
        <EmptyState
          title="Não foi possível carregar as proposições"
          description={erro}
          icon={<AlertCircle className="w-10 h-10 text-rose-400" />}
        />
      ) : proposicoes.length === 0 ? (
        <EmptyState
          title="Nenhuma proposição encontrada"
          description="Tente ajustar os filtros para ampliar a busca."
          icon={<FileText className="w-10 h-10" />}
        />
      ) : (
        <>
          <div className="space-y-3">
            {proposicoes.map((p) => (
              <ProposicaoCard key={p.id} proposicao={p} />
            ))}
          </div>
          <Pagination
            pagina={pagina}
            total={total}
            itensPorPagina={ITENS_POR_PAGINA}
            onChange={setPagina}
          />
        </>
      )}
    </div>
  )
}
