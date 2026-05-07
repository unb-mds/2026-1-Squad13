import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Mail, Scale, CheckCircle } from 'lucide-react'
import { recuperarSenhaApi } from '@/shared/lib/api'
import { Button, Input } from '@/shared/ui'

export function RecuperarSenhaForm() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [enviado, setEnviado] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    await recuperarSenhaApi(email)
    setLoading(false)
    setEnviado(true)
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
          {enviado ? (
            <div className="text-center py-4">
              <CheckCircle className="w-12 h-12 text-volt-400 mx-auto mb-4" />
              <h2 className="font-display font-700 text-xl text-white mb-2">E-mail enviado!</h2>
              <p className="text-ink-400 text-sm mb-6">Verifique sua caixa de entrada para instruções de recuperação.</p>
              <Link to="/login" className="text-volt-300 hover:text-volt-200 text-sm font-medium">← Voltar ao login</Link>
            </div>
          ) : (
            <>
              <h2 className="font-display font-700 text-xl text-white mb-2">Recuperar senha</h2>
              <p className="text-ink-400 text-sm mb-6">Informe seu e-mail para receber o link de recuperação.</p>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Input label="E-mail" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="seu@email.gov.br" leftIcon={<Mail className="w-4 h-4" />} required />
                <Button type="submit" loading={loading} className="w-full justify-center py-3">
                  {loading ? 'Enviando...' : 'Enviar link de recuperação'}
                </Button>
              </form>
              <p className="mt-6 text-center text-sm text-ink-400">
                <Link to="/login" className="text-volt-300 hover:text-volt-200 font-medium">← Voltar ao login</Link>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
