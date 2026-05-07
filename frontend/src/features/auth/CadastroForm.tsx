import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Mail, Lock, User, Scale } from 'lucide-react'
import { useAuth } from '@/app/providers/AuthProvider'
import { cadastroApi } from '@/shared/lib/api'
import { Button, Input } from '@/shared/ui'

export function CadastroForm() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [confirmar, setConfirmar] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (senha !== confirmar) { setError('As senhas não conferem.'); return }
    if (senha.length < 6) { setError('A senha deve ter pelo menos 6 caracteres.'); return }
    setError('')
    setLoading(true)
    try {
      const { token, user } = await cadastroApi(nome, email, senha)
      login(user, token)
      navigate('/dashboard')
    } catch {
      setError('Erro ao criar conta. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-ink-900 flex items-center justify-center px-4">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:48px_48px]" />
      <div className="relative w-full max-w-md animate-slide-up">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-volt-400 rounded-2xl mb-4">
            <Scale className="w-7 h-7 text-ink-900" />
          </div>
          <h1 className="font-display font-800 text-3xl text-white">LexTrack</h1>
        </div>

        <div className="bg-ink-800 border border-ink-700/50 rounded-2xl p-8">
          <h2 className="font-display font-700 text-xl text-white mb-6">Criar nova conta</h2>

          {error && (
            <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/25 rounded-lg text-rose-400 text-sm">{error}</div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input label="Nome completo" value={nome} onChange={(e) => setNome(e.target.value)} placeholder="Seu nome" leftIcon={<User className="w-4 h-4" />} required />
            <Input label="E-mail" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="seu@email.gov.br" leftIcon={<Mail className="w-4 h-4" />} required />
            <Input label="Senha" type="password" value={senha} onChange={(e) => setSenha(e.target.value)} placeholder="••••••••" leftIcon={<Lock className="w-4 h-4" />} required />
            <Input label="Confirmar senha" type="password" value={confirmar} onChange={(e) => setConfirmar(e.target.value)} placeholder="••••••••" leftIcon={<Lock className="w-4 h-4" />} required />
            <Button type="submit" loading={loading} className="w-full justify-center py-3">
              {loading ? 'Criando conta...' : 'Criar conta'}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-ink-400">
            Já tem conta?{' '}
            <Link to="/login" className="text-volt-300 hover:text-volt-200 font-medium">Entrar</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
