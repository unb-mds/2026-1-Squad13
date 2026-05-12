import { useState, useCallback, useEffect, type ReactNode } from 'react'
import { AUTH_TOKEN_KEY, AUTH_USER_KEY, AUTH_EXPIRES_KEY, TOKEN_EXPIRATION_MS } from '@/shared/constants'
import type { AuthState, User } from '@/shared/types'
import { AuthContext } from './AuthContext'

/**
 * Provedor de Autenticação.
 * Exporta apenas o componente para manter compatibilidade total com Fast Refresh.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    try {
      const token = localStorage.getItem(AUTH_TOKEN_KEY)
      const userStr = localStorage.getItem(AUTH_USER_KEY)
      const expiresAt = Number(localStorage.getItem(AUTH_EXPIRES_KEY))
      if (token && userStr && expiresAt && Date.now() < expiresAt) {
        return { token, user: JSON.parse(userStr), isAuthenticated: true, expiresAt }
      }
    } catch { /* ignore localStorage read errors */ }
    return { token: null, user: null, isAuthenticated: false, expiresAt: null }
  })

  const logout = useCallback(() => {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    localStorage.removeItem(AUTH_USER_KEY)
    localStorage.removeItem(AUTH_EXPIRES_KEY)
    setState({ user: null, token: null, isAuthenticated: false, expiresAt: null })
  }, [])

  useEffect(() => {
    if (!state.expiresAt) return
    const remaining = state.expiresAt - Date.now()
    if (remaining <= 0) { logout(); return }
    const timer = setTimeout(() => logout(), remaining)
    return () => clearTimeout(timer)
  }, [state.expiresAt, logout])

  const login = useCallback((user: User, token: string) => {
    const expiresAt = Date.now() + TOKEN_EXPIRATION_MS
    localStorage.setItem(AUTH_TOKEN_KEY, token)
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user))
    localStorage.setItem(AUTH_EXPIRES_KEY, String(expiresAt))
    setState({ user, token, isAuthenticated: true, expiresAt })
  }, [])

  return <AuthContext.Provider value={{ ...state, login, logout }}>{children}</AuthContext.Provider>
}
