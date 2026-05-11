import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, ExternalLink, Clock, Building2, User, Calendar,
  AlertTriangle, CheckCircle, FileText
} from 'lucide-react'
import { obterProposicao, obterMovimentacoes } from '@/shared/lib/api'
import type { Proposicao, MovimentacaoTramitacao } from '@/shared/types'
import { formatarData, formatarDataCurta, formatarTempo, corStatus, corTipo, calcularDiasEntreatas } from '@/shared/lib/utils'
import { TimelineTramitacao } from '@/features/tramitacoes/TimelineTramitacao'
import { CardPrevisaoIA } from '@/features/tramitacoes/CardPrevisaoIA'
import { Card, CardHeader, CardBody, Spinner } from '@/shared/ui'

function InfoRow({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-start gap-3 py-3 border-b border-ink-700/40 last:border-0">
      <div className="p-1.5 bg-ink-700/50 rounded-lg text-ink-400 shrink-0">{icon}</div>
      <div>
        <p className="text-xs text-ink-500 font-medium">{label}</p>
        <p className="text-sm text-ink-200 mt-0.5">{value}</p>
      </div>
    </div>
  )
}

export function DetalheProposicaoPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [proposicao, setProposicao] = useState<Proposicao | null>(null)
  const [movimentacoes, setMovimentacoes] = useState<MovimentacaoTramitacao[]>([])
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    Promise.all([obterProposicao(id), obterMovimentacoes(id)])
      .then(([prop, movs]) => {
        if (!prop) { setNotFound(true); return }
        setProposicao(prop)
        setMovimentacoes(movs)
      })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Spinner className="w-8 h-8" />
    </div>
  )

  if (notFound || !proposicao) return (
    <div className="p-6 text-center">
      <FileText className="w-12 h-12 text-ink-600 mx-auto mb-4" />
      <p className="text-white font-medium mb-1">Proposição não encontrada</p>
      <button onClick={() => navigate('/proposicoes')} className="text-sm text-volt-300 hover:text-volt-200">
        Voltar à lista
      </button>
    </div>
  )

  const emTramitacao = ['Em tramitação', 'Em análise', 'Aguardando votação'].includes(proposicao.status)
  const diasAcumulados = emTramitacao
    ? calcularDiasEntreatas(proposicao.dataApresentacao)
    : proposicao.tempoTotalDias

  return (
    <div className="p-6 animate-fade-in">
      {/* Back button */}
      <button
        onClick={() => navigate('/proposicoes')}
        className="flex items-center gap-2 text-sm text-ink-400 hover:text-volt-300 transition-colors mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Voltar às proposições
      </button>

      {/* Header */}
      <div className="bg-ink-800 border border-ink-700/50 rounded-xl p-6 mb-5">
        <div className="flex flex-wrap items-start gap-3 mb-4">
          <span className={`px-2.5 py-1.5 rounded-lg text-sm font-display font-700 ${corTipo(proposicao.tipo)}`}>
            {proposicao.tipo}
          </span>
          <div className="flex-1">
            <h1 className="font-display font-700 text-xl text-white leading-tight">
              {proposicao.tipo} {proposicao.numero}/{proposicao.ano}
            </h1>
            <p className="text-sm text-ink-400 mt-1">{proposicao.orgaoOrigem}</p>
          </div>
          <span className={`px-3 py-1.5 rounded-lg text-sm font-medium border ${corStatus(proposicao.status)}`}>
            {proposicao.status}
          </span>
        </div>

        {/* Ementa */}
        <div className="bg-ink-700/30 rounded-lg p-4 mb-4">
          <p className="text-xs text-ink-500 font-medium mb-2">EMENTA</p>
          <p className="text-sm text-ink-200 leading-relaxed">{proposicao.ementa}</p>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1.5">
          {proposicao.tags.map((tag) => (
            <span key={tag} className="px-2 py-1 bg-ink-700/50 text-ink-400 text-xs rounded-md border border-ink-700/50">
              #{tag}
            </span>
          ))}
        </div>

        {/* Link oficial */}
        {proposicao.linkOficial && (
          <a
            href={proposicao.linkOficial}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 mt-4 text-xs text-volt-300 hover:text-volt-200 transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            Acessar no portal oficial
          </a>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Sidebar info */}
        <div className="space-y-5">
          {/* Detalhes */}
          <Card>
            <CardHeader>
              <p className="text-sm font-medium text-ink-200">Informações</p>
            </CardHeader>
            <CardBody className="py-0 px-5">
              <InfoRow icon={<User className="w-3.5 h-3.5" />} label="Autor" value={proposicao.autor} />
              <InfoRow icon={<Building2 className="w-3.5 h-3.5" />} label="Órgão/Comissão atual" value={proposicao.orgaoAtual} />
              <InfoRow icon={<Calendar className="w-3.5 h-3.5" />} label="Apresentação" value={formatarData(proposicao.dataApresentacao)} />
              <InfoRow icon={<Clock className="w-3.5 h-3.5" />} label="Última movimentação" value={formatarDataCurta(proposicao.dataUltimaMovimentacao)} />
            </CardBody>
          </Card>

          {/* Tempo de tramitação */}
          <Card className={proposicao.temAtraso ? 'border-rose-500/25 bg-rose-500/5' : ''}>
            <CardBody>
              <div className="flex items-center gap-2 mb-2">
                {proposicao.temAtraso
                  ? <AlertTriangle className="w-4 h-4 text-rose-400" />
                  : <CheckCircle className="w-4 h-4 text-volt-400" />
                }
                <p className="text-sm font-medium text-white">Tempo de tramitação</p>
              </div>
              <p className={`text-3xl font-display font-700 mb-1 ${proposicao.temAtraso ? 'text-rose-300' : 'text-volt-300'}`}>
                {formatarTempo(diasAcumulados)}
              </p>
              {emTramitacao && (
                <p className="text-xs text-ink-400">Acumulado até hoje</p>
              )}
              {proposicao.temAtraso && (
                <p className="text-xs text-rose-400 mt-2 font-medium">⚠ Atraso significativo detectado</p>
              )}
            </CardBody>
          </Card>

          {/* Previsão IA */}
          <CardPrevisaoIA
            temPrevisao={proposicao.temPrevisaoIA}
            diasEstimados={proposicao.previsaoAprovacaoDias}
            status={proposicao.status}
          />
        </div>

        {/* Timeline */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <p className="text-sm font-medium text-ink-200">Histórico de Tramitação</p>
              <p className="text-xs text-ink-400 mt-0.5">Da movimentação mais recente à mais antiga</p>
            </CardHeader>
            <CardBody>
              <TimelineTramitacao movimentacoes={movimentacoes} />
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  )
}
