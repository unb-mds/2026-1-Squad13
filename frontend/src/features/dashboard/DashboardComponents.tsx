import { useState, useEffect } from 'react'
import { Clock, FileText, AlertTriangle, Building2, TrendingUp, CheckCircle, XCircle } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import {
  obterMetricas, obterDadosTipo, obterDadosComissao, obterDadosStatus,
} from '@/shared/lib/api'
import type { MetricasDashboard, DadosGraficoTipo, DadosGraficoComissao, DadosGraficoStatus } from '@/shared/types'
import { formatarTempo } from '@/shared/lib/utils'
import { KpiCard, Card, CardHeader, CardBody, Spinner } from '@/shared/ui'

const COLORS = ['#c2ff3d', '#6366f1', '#f59e0b', '#fb7185', '#22d3ee', '#a78bfa', '#34d399']

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: { value: number }[]; label?: string }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-ink-700 border border-ink-600 rounded-lg px-3 py-2 text-sm shadow-xl">
      <p className="text-ink-300 mb-1">{label}</p>
      <p className="text-white font-medium">{formatarTempo(payload[0].value)}</p>
    </div>
  )
}

export function DashboardMetricas() {
  const [metricas, setMetricas] = useState<MetricasDashboard | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    obterMetricas().then(setMetricas).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="bg-ink-800 border border-ink-700/50 rounded-xl p-5 h-28 animate-pulse" />
      ))}
    </div>
  )

  if (!metricas) return null

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <KpiCard
        label="Tempo médio de tramitação"
        value={formatarTempo(metricas.tempoMedioTramitacao)}
        sub="por proposição"
        icon={<Clock className="w-4 h-4" />}
      />
      <KpiCard
        label="Total de proposições"
        value={metricas.totalProposicoes}
        sub={`${metricas.totalAprovadas} aprovadas · ${metricas.totalEmTramitacao} em curso`}
        icon={<FileText className="w-4 h-4" />}
      />
      <KpiCard
        label="Com atraso significativo"
        value={metricas.proposicoesComAtraso}
        sub="mais de 180 dias paradas"
        highlight
        icon={<AlertTriangle className="w-4 h-4" />}
      />
      <KpiCard
        label="Comissão mais lenta"
        value={metricas.comissaoMaiorTempo}
        sub={`Média: ${formatarTempo(metricas.comissaoMaiorTempoMedia)}`}
        icon={<Building2 className="w-4 h-4" />}
      />
    </div>
  )
}

export function DashboardGraficos() {
  const [dadosTipo, setDadosTipo] = useState<DadosGraficoTipo[]>([])
  const [dadosComissao, setDadosComissao] = useState<DadosGraficoComissao[]>([])
  const [dadosStatus, setDadosStatus] = useState<DadosGraficoStatus[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([obterDadosTipo(), obterDadosComissao(), obterDadosStatus()])
      .then(([tipo, comissao, status]) => {
        setDadosTipo(tipo)
        setDadosComissao(comissao)
        setDadosStatus(status)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="bg-ink-800 border border-ink-700/50 rounded-xl h-72 animate-pulse" />
      ))}
    </div>
  )

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {/* Tempo médio por tipo */}
      <Card>
        <CardHeader>
          <p className="text-sm font-medium text-ink-200">Tempo médio por tipo</p>
          <p className="text-xs text-ink-400 mt-0.5">Em dias de tramitação</p>
        </CardHeader>
        <CardBody>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={dadosTipo} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2e2e52" />
              <XAxis dataKey="tipo" tick={{ fill: '#8080b0', fontSize: 12 }} />
              <YAxis tick={{ fill: '#8080b0', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="tempoMedio" fill="#c2ff3d" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardBody>
      </Card>

      {/* Tempo por comissão */}
      <Card>
        <CardHeader>
          <p className="text-sm font-medium text-ink-200">Tempo médio por comissão</p>
          <p className="text-xs text-ink-400 mt-0.5">Dias de análise por órgão</p>
        </CardHeader>
        <CardBody>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={dadosComissao} layout="vertical" margin={{ top: 0, right: 0, left: 20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2e2e52" />
              <XAxis type="number" tick={{ fill: '#8080b0', fontSize: 11 }} />
              <YAxis dataKey="comissao" type="category" tick={{ fill: '#8080b0', fontSize: 11 }} width={50} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="tempoMedio" fill="#6366f1" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardBody>
      </Card>

      {/* Distribuição por status */}
      <Card>
        <CardHeader>
          <p className="text-sm font-medium text-ink-200">Distribuição por status</p>
          <p className="text-xs text-ink-400 mt-0.5">Proporção atual do acervo</p>
        </CardHeader>
        <CardBody>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={dadosStatus} dataKey="quantidade" nameKey="status" cx="50%" cy="50%" outerRadius={70} innerRadius={35}>
                {dadosStatus.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(v: number, name: string) => [`${v} proposições`, name]} contentStyle={{ background: '#1e1e38', border: '1px solid #3d3d6b', borderRadius: 8 }} />
              <Legend formatter={(v) => <span style={{ color: '#8080b0', fontSize: 11 }}>{v}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </CardBody>
      </Card>
    </div>
  )
}

export function DashboardResumoStatus() {
  const [metricas, setMetricas] = useState<MetricasDashboard | null>(null)

  useEffect(() => {
    obterMetricas().then(setMetricas)
  }, [])

  if (!metricas) return null

  return (
    <div className="grid grid-cols-3 gap-3">
      <div className="flex items-center gap-3 bg-ink-800 border border-ink-700/50 rounded-xl p-4">
        <div className="p-2 rounded-lg bg-volt-400/10"><TrendingUp className="w-4 h-4 text-volt-400" /></div>
        <div>
          <p className="text-2xl font-display font-700 text-white">{metricas.totalEmTramitacao}</p>
          <p className="text-xs text-ink-400">Em tramitação</p>
        </div>
      </div>
      <div className="flex items-center gap-3 bg-ink-800 border border-ink-700/50 rounded-xl p-4">
        <div className="p-2 rounded-lg bg-emerald-500/10"><CheckCircle className="w-4 h-4 text-emerald-400" /></div>
        <div>
          <p className="text-2xl font-display font-700 text-white">{metricas.totalAprovadas}</p>
          <p className="text-xs text-ink-400">Aprovadas/Sancionadas</p>
        </div>
      </div>
      <div className="flex items-center gap-3 bg-ink-800 border border-ink-700/50 rounded-xl p-4">
        <div className="p-2 rounded-lg bg-rose-500/10"><XCircle className="w-4 h-4 text-rose-400" /></div>
        <div>
          <p className="text-2xl font-display font-700 text-white">{metricas.totalRejeitadas}</p>
          <p className="text-xs text-ink-400">Rejeitadas/Arquivadas</p>
        </div>
      </div>
    </div>
  )
}
