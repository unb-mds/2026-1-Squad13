import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Download } from 'lucide-react'
import { obterGargalos, obterComparacaoTemas } from '@/shared/lib/api'
import type { GargaloInstitucional, ComparacaoTema } from '@/shared/types'
import { Card, CardHeader, CardBody, Badge, Button, Spinner } from '@/shared/ui'

export function TabelaGargalos() {
  const [gargalos, setGargalos] = useState<GargaloInstitucional[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    obterGargalos().then(setGargalos).finally(() => setLoading(false))
  }, [])

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-ink-200">Gargalos Institucionais</p>
          <p className="text-xs text-ink-400 mt-0.5">Órgãos com maior tempo médio de análise</p>
        </div>
        <AlertTriangle className="w-4 h-4 text-amber-400" />
      </CardHeader>
      <CardBody className="p-0">
        {loading ? (
          <div className="flex justify-center py-8"><Spinner className="w-5 h-5" /></div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-ink-700/50">
                <th className="text-left text-xs text-ink-400 font-medium px-5 py-3">Órgão</th>
                <th className="text-right text-xs text-ink-400 font-medium px-5 py-3">Tempo médio</th>
                <th className="text-right text-xs text-ink-400 font-medium px-5 py-3">Proposições</th>
                <th className="text-right text-xs text-ink-400 font-medium px-5 py-3">Taxa de atraso</th>
              </tr>
            </thead>
            <tbody>
              {gargalos.map((g, i) => (
                <tr key={g.orgao} className={`border-b border-ink-700/30 hover:bg-ink-700/20 transition-colors ${i === 0 ? 'bg-rose-500/5' : ''}`}>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-white">{g.orgao}</span>
                      {i === 0 && <Badge variant="danger">Crítico</Badge>}
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <span className={`text-sm font-mono font-medium ${i === 0 ? 'text-rose-400' : 'text-ink-200'}`}>
                      {g.tempoMedioMeses} meses
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <span className="text-sm text-ink-300">{g.quantidadeProposicoes}</span>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <span className={`text-sm font-medium ${g.taxaAtraso >= 50 ? 'text-rose-400' : g.taxaAtraso >= 30 ? 'text-amber-400' : 'text-emerald-400'}`}>
                      {g.taxaAtraso}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </CardBody>
    </Card>
  )
}

function VelocidadeIcon({ v }: { v: 'rapido' | 'medio' | 'lento' }) {
  if (v === 'rapido') return <TrendingUp className="w-4 h-4 text-emerald-400" />
  if (v === 'lento') return <TrendingDown className="w-4 h-4 text-rose-400" />
  return <Minus className="w-4 h-4 text-amber-400" />
}

export function ComparacaoTemas() {
  const [temas, setTemas] = useState<ComparacaoTema[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    obterComparacaoTemas().then(setTemas).finally(() => setLoading(false))
  }, [])

  const rapidos = temas.filter((t) => t.velocidade === 'rapido')
  const lentos = temas.filter((t) => t.velocidade === 'lento')
  const medios = temas.filter((t) => t.velocidade === 'medio')

  return (
    <Card>
      <CardHeader>
        <p className="text-sm font-medium text-ink-200">Comparação por Tema</p>
        <p className="text-xs text-ink-400 mt-0.5">Temas que avançam rápido vs. temas travados</p>
      </CardHeader>
      <CardBody>
        {loading ? (
          <div className="flex justify-center py-8"><Spinner className="w-5 h-5" /></div>
        ) : (
          <div className="grid grid-cols-3 gap-4">
            {/* Rápidos */}
            <div>
              <div className="flex items-center gap-1.5 mb-3">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                <p className="text-xs font-medium text-emerald-400">Avançam rápido</p>
              </div>
              <div className="space-y-2">
                {rapidos.map((t) => (
                  <div key={t.tema} className="bg-emerald-500/8 border border-emerald-500/20 rounded-lg p-3">
                    <p className="text-sm text-white font-medium">{t.tema}</p>
                    <p className="text-xs text-ink-400 mt-0.5">{t.tempoMedioDias} dias · {t.taxaAprovacao}% aprovação</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Médios */}
            <div>
              <div className="flex items-center gap-1.5 mb-3">
                <Minus className="w-4 h-4 text-amber-400" />
                <p className="text-xs font-medium text-amber-400">Ritmo moderado</p>
              </div>
              <div className="space-y-2">
                {medios.map((t) => (
                  <div key={t.tema} className="bg-amber-500/8 border border-amber-500/20 rounded-lg p-3">
                    <p className="text-sm text-white font-medium">{t.tema}</p>
                    <p className="text-xs text-ink-400 mt-0.5">{t.tempoMedioDias} dias · {t.taxaAprovacao}% aprovação</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Lentos */}
            <div>
              <div className="flex items-center gap-1.5 mb-3">
                <TrendingDown className="w-4 h-4 text-rose-400" />
                <p className="text-xs font-medium text-rose-400">Temas travados</p>
              </div>
              <div className="space-y-2">
                {lentos.map((t) => (
                  <div key={t.tema} className="bg-rose-500/8 border border-rose-500/20 rounded-lg p-3">
                    <p className="text-sm text-white font-medium">{t.tema}</p>
                    <p className="text-xs text-ink-400 mt-0.5">{t.tempoMedioDias} dias · {t.taxaAprovacao}% aprovação</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  )
}

export function BotaoExportar() {
  const [loading, setLoading] = useState(false)
  const [exportado, setExportado] = useState(false)

  const handleExportar = async () => {
    setLoading(true)
    await new Promise((r) => setTimeout(r, 1500))
    setLoading(false)
    setExportado(true)
    setTimeout(() => setExportado(false), 3000)
  }

  return (
    <Button
      variant="secondary"
      loading={loading}
      leftIcon={<Download className="w-4 h-4" />}
      onClick={handleExportar}
    >
      {exportado ? '✓ Relatório exportado!' : 'Exportar relatório'}
    </Button>
  )
}
