import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Mail, Lock, Eye, EyeOff, Scale } from 'lucide-react'
import { useAuth } from '@/app/providers/AuthProvider'
import { loginApi } from '@/shared/lib/api'
import { Button, Input } from '@/shared/ui'

export function LoginForm() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('demo@lextrack.gov.br')
  const [senha, setSenha] = useState('demo123')
  const [showSenha, setShowSenha] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { token, user } = await loginApi(email, senha)
      login(user, token)
      navigate('/dashboard')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Erro ao autenticar.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-ink-900 flex items-center justify-center px-4">
      {/* Background grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:48px_48px]" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-volt-400/5 blur-3xl rounded-full" />

      <div className="relative w-full max-w-md animate-slide-up">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-volt-400 rounded-2xl mb-4 shadow-lg shadow-volt-400/20">
            <Scale className="w-7 h-7 text-ink-900" />
          </div>
          <h1 className="font-display font-800 text-3xl text-white">LexTrack</h1>
          <p className="text-ink-400 text-sm mt-1">Monitoramento de Tramitação Legislativa</p>
        </div>

        <div className="bg-ink-800 border border-ink-700/50 rounded-2xl p-8 shadow-xl">
          <h2 className="font-display font-700 text-xl text-white mb-6">Acesse sua conta</h2>

          {error && (
            <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/25 rounded-lg text-rose-400 text-sm">
              {error}
            </div>
          )}

          {/* Demo hint */}
          <div className="mb-5 p-3 bg-volt-400/8 border border-volt-400/20 rounded-lg">
            <p className="text-volt-300 text-xs font-medium">Acesso de demonstração:</p>
            <p className="text-ink-300 text-xs mt-0.5 font-mono">demo@lextrack.gov.br / demo123</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="E-mail"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seu@email.gov.br"
              leftIcon={<Mail className="w-4 h-4" />}
              required
            />
            <div className="relative">
              <Input
                label="Senha"
                type={showSenha ? 'text' : 'password'}
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                placeholder="••••••••"
                leftIcon={<Lock className="w-4 h-4" />}
                required
              />
              <button
                type="button"
                onClick={() => setShowSenha(!showSenha)}
                className="absolute right-3 top-9 text-ink-400 hover:text-ink-200"
              >
                {showSenha ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>

            <div className="flex justify-end">
              <Link to="/recuperar-senha" className="text-xs text-ink-400 hover:text-volt-300 transition-colors">
                Esqueceu a senha?
              </Link>
            </div>

            <Button type="submit" loading={loading} className="w-full justify-center py-3">
              {loading ? 'Autenticando...' : 'Entrar'}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-ink-400">
            Não tem conta?{' '}
            <Link to="/cadastro" className="text-volt-300 hover:text-volt-200 font-medium transition-colors">
              Cadastre-se
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
