import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '../providers/AuthProvider'
import { AppLayout } from '../layouts/AppLayout'
import { LoginPage } from '@/pages/login-page'
import { CadastroPage } from '@/pages/cadastro-page'
import { RecuperarSenhaPage } from '@/pages/recuperar-senha-page'
import { DashboardPage } from '@/pages/dashboard-page'
import { ConsultaProposicoesPage } from '@/pages/consulta-proposicoes-page'
import { DetalheProposicaoPage } from '@/pages/detalhe-proposicao-page'
import { RelatoriosPage } from '@/pages/relatorios-page'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/cadastro" element={<CadastroPage />} />
        <Route path="/recuperar-senha" element={<RecuperarSenhaPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <AppLayout />
            </PrivateRoute>
          }
        >
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
