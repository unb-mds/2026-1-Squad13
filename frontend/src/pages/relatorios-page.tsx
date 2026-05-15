import { useState, useEffect } from 'react'
import { BarChart3, AlertTriangle, TrendingUp, FileDown } from 'lucide-react'
import { TabelaGargalos, ComparacaoTemas, BotaoExportar } from '@/features/relatorios/RelatorioComponents'
import { Card, CardBody } from '@/shared/ui'
import { obterGargalos, obterComparacaoTemas } from '@/shared/lib/api'
import type { GargaloInstitucional, ComparacaoTema } from '@/shared/types'

export function RelatoriosPage() {
  const [gargalos, setGargalos] = useState<GargaloInstitucional[]>([])
  const [temas, setTemas] = useState<ComparacaoTema[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([obterGargalos(), obterComparacaoTemas()])
      .then(([g, t]) => {
        setGargalos(g)
        setTemas(t)
      })
      .finally(() => setLoading(false))
  }, [])

  const principalGargalo = gargalos[0]
  const maisRapido = [...temas].sort((a, b) => a.tempoMedioDias - b.tempoMedioDias)[0]
  const maisTravado = [...temas].sort((a, b) => b.tempoMedioDias - a.tempoMedioDias)[0]

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-volt-400" />
          <h1 className="font-display font-700 text-2xl text-white">Relatórios Analíticos</h1>
        </div>
        <BotaoExportar />
      </div>

      {/* Resumo top */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="border-rose-500/25 bg-rose-500/5">
          <CardBody className="flex items-start gap-3">
            <div className="p-2 bg-rose-500/15 rounded-lg shrink-0">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
            </div>
            <div>
              <p className="text-xs text-ink-400 font-medium uppercase tracking-wider">Principal gargalo</p>
              <p className="text-lg font-display font-700 text-white mt-0.5">
                {loading ? '...' : principalGargalo?.orgao || 'N/A'}
              </p>
              <p className="text-xs text-rose-400">
                {loading ? 'Carregando...' : principalGargalo ? `${principalGargalo.tempoMedioMeses} meses em média · ${principalGargalo.taxaAtraso}% de atraso` : 'Sem dados'}
              </p>
            </div>
          </CardBody>
        </Card>

        <Card className="border-volt-400/25 bg-volt-400/5">
          <CardBody className="flex items-start gap-3">
            <div className="p-2 bg-volt-400/15 rounded-lg shrink-0">
              <TrendingUp className="w-4 h-4 text-volt-400" />
            </div>
            <div>
              <p className="text-xs text-ink-400 font-medium uppercase tracking-wider">Tema mais rápido</p>
              <p className="text-lg font-display font-700 text-white mt-0.5">
                {loading ? '...' : maisRapido?.tema || 'N/A'}
              </p>
              <p className="text-xs text-volt-400">
                {loading ? 'Carregando...' : maisRapido ? `${maisRapido.tempoMedioDias} dias · ${maisRapido.taxaAprovacao}% de aprovação` : 'Sem dados'}
              </p>
            </div>
          </CardBody>
        </Card>

        <Card className="border-amber-500/25 bg-amber-500/5">
          <CardBody className="flex items-start gap-3">
            <div className="p-2 bg-amber-500/15 rounded-lg shrink-0">
              <FileDown className="w-4 h-4 text-amber-400" />
            </div>
            <div>
              <p className="text-xs text-ink-400 font-medium uppercase tracking-wider">Tema mais travado</p>
              <p className="text-lg font-display font-700 text-white mt-0.5">
                {loading ? '...' : maisTravado?.tema || 'N/A'}
              </p>
              <p className="text-xs text-amber-400">
                {loading ? 'Carregando...' : maisTravado ? `${maisTravado.tempoMedioDias} dias · ${maisTravado.taxaAprovacao}% de aprovação` : 'Sem dados'}
              </p>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Gargalos */}
      <TabelaGargalos />

      {/* Comparação temas */}
      <ComparacaoTemas />
    </div>
  )
}
