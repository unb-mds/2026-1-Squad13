import { createContext, useContext } from 'react'
import type { AuthState, User } from '@/shared/types'

export interface AuthContextValue extends AuthState {
  login: (user: User, token: string) => void
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)

/**
 * Hook para acessar o contexto de autenticação de forma segura.
 */
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
