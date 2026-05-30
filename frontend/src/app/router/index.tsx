import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppLayout } from '../layouts/AppLayout'
import { DashboardPage } from '@/pages/dashboard-page'
import { ConsultaProposicoesPage } from '@/pages/consulta-proposicoes-page'
import { DetalheProposicaoPage } from '@/pages/detalhe-proposicao-page'
import { RelatoriosPage } from '@/pages/relatorios-page'

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="proposicoes" element={<ConsultaProposicoesPage />} />
          <Route path="proposicoes/:id" element={<DetalheProposicaoPage />} />
          <Route path="relatorios" element={<RelatoriosPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
