import { BarChart3, AlertTriangle, TrendingUp, FileDown } from 'lucide-react'
import { TabelaGargalos, ComparacaoTemas, BotaoExportar } from '@/features/relatorios/RelatorioComponents'
import { Card, CardBody } from '@/shared/ui'

export function RelatoriosPage() {
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
              <p className="text-lg font-display font-700 text-white mt-0.5">CCJ</p>
              <p className="text-xs text-rose-400">22 meses em média · 62% de atraso</p>
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
              <p className="text-lg font-display font-700 text-white mt-0.5">Tributário</p>
              <p className="text-xs text-volt-400">215 dias · 78% de aprovação</p>
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
              <p className="text-lg font-display font-700 text-white mt-0.5">Internet & Mídia</p>
              <p className="text-xs text-amber-400">1322 dias · 12% de aprovação</p>
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
