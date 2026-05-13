import type { ReactNode, ButtonHTMLAttributes, InputHTMLAttributes, SelectHTMLAttributes } from 'react'
import { Loader2 } from 'lucide-react'

// --- Card ---
export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`bg-ink-800 border border-ink-700/50 rounded-xl ${className}`}>{children}</div>
  )
}

export function CardHeader({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`px-5 py-4 border-b border-ink-700/50 ${className}`}>{children}</div>
}

export function CardBody({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`px-5 py-4 ${className}`}>{children}</div>
}

// --- Badge ---
type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'volt'
const badgeClasses: Record<BadgeVariant, string> = {
  default: 'bg-ink-600/50 text-ink-300 border-ink-600/50',
  success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25',
  warning: 'bg-amber-500/15 text-amber-400 border-amber-500/25',
  danger: 'bg-rose-500/15 text-rose-400 border-rose-500/25',
  info: 'bg-blue-500/15 text-blue-400 border-blue-500/25',
  volt: 'bg-volt-400/15 text-volt-300 border-volt-400/25',
}

export function Badge({ children, variant = 'default', className = '' }: { children: ReactNode; variant?: BadgeVariant; className?: string }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium border ${badgeClasses[variant]} ${className}`}>
      {children}
    </span>
  )
}

// --- Button ---
type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'
const btnClasses: Record<ButtonVariant, string> = {
  primary: 'bg-volt-400 text-ink-900 hover:bg-volt-300 font-semibold',
  secondary: 'bg-ink-700 text-white hover:bg-ink-600 border border-ink-600',
  ghost: 'text-ink-300 hover:text-white hover:bg-ink-700/60',
  danger: 'bg-rose-500/15 text-rose-400 hover:bg-rose-500/25 border border-rose-500/25',
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  loading?: boolean
  leftIcon?: ReactNode
}

export function Button({ variant = 'primary', loading, leftIcon, children, className = '', disabled, ...props }: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed ${btnClasses[variant]} ${className}`}
      {...props}
    >
      {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : leftIcon}
      {children}
    </button>
  )
}

// --- Input ---
interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  leftIcon?: ReactNode
}

export function Input({ label, error, leftIcon, className = '', ...props }: InputProps) {
  return (
    <div className="w-full">
      {label && <label className="block text-sm text-ink-300 mb-1.5 font-medium">{label}</label>}
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-400">{leftIcon}</div>
        )}
        <input
          className={`w-full bg-ink-700/50 border border-ink-600/50 text-white placeholder-ink-400 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-volt-400/50 focus:border-volt-400/50 transition-all ${leftIcon ? 'pl-9' : ''} ${error ? 'border-rose-500/50' : ''} ${className}`}
          {...props}
        />
      </div>
      {error && <p className="mt-1.5 text-xs text-rose-400">{error}</p>}
    </div>
  )
}

// --- Select ---
interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
}

export function Select({ label, children, className = '', ...props }: SelectProps) {
  return (
    <div className="w-full">
      {label && <label className="block text-sm text-ink-300 mb-1.5 font-medium">{label}</label>}
      <select
        className={`w-full bg-ink-700/50 border border-ink-600/50 text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-volt-400/50 focus:border-volt-400/50 transition-all appearance-none ${className}`}
        {...props}
      >
        {children}
      </select>
    </div>
  )
}

// --- Spinner ---
export function Spinner({ className = '' }: { className?: string }) {
  return <Loader2 role="status" aria-label="Carregando" className={`animate-spin text-volt-400 ${className}`} />
}

// --- Empty State ---
export function EmptyState({ title, description, icon }: { title: string; description?: string; icon?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && <div className="mb-4 text-ink-500">{icon}</div>}
      <p className="text-ink-200 font-medium">{title}</p>
      {description && <p className="mt-1 text-sm text-ink-400 max-w-sm">{description}</p>}
    </div>
  )
}

// --- KPI Card ---
export function KpiCard({ label, value, sub, highlight, icon }: {
  label: string
  value: string | number
  sub?: string
  highlight?: boolean
  icon?: ReactNode
}) {
  return (
    <Card className={`p-5 ${highlight ? 'border-rose-500/30 bg-rose-500/5' : ''}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-ink-400 font-medium uppercase tracking-wider">{label}</p>
          <p className={`mt-1.5 text-3xl font-display font-700 ${highlight ? 'text-rose-400' : 'text-white'}`}>{value}</p>
          {sub && <p className="mt-1 text-xs text-ink-400">{sub}</p>}
        </div>
        {icon && (
          <div className={`p-2 rounded-lg ${highlight ? 'bg-rose-500/15 text-rose-400' : 'bg-ink-700/50 text-ink-400'}`}>
            {icon}
          </div>
        )}
      </div>
    </Card>
  )
}

// --- Pagination ---
export function Pagination({ pagina, total, itensPorPagina, onChange }: {
  pagina: number
  total: number
  itensPorPagina: number
  onChange: (p: number) => void
}) {
  const totalPaginas = Math.ceil(total / itensPorPagina)
  if (totalPaginas <= 1) return null
  const inicio = (pagina - 1) * itensPorPagina + 1
  const fim = Math.min(pagina * itensPorPagina, total)

  return (
    <div className="flex items-center justify-between px-1 mt-4">
      <p className="text-xs text-ink-400">
        Exibindo <span className="text-ink-200">{inicio}–{fim}</span> de <span className="text-ink-200">{total}</span>
      </p>
      <div className="flex gap-1">
        <button
          onClick={() => onChange(pagina - 1)}
          disabled={pagina === 1}
          className="px-3 py-1.5 rounded-lg text-xs text-ink-300 hover:text-white hover:bg-ink-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          ← Anterior
        </button>
        {Array.from({ length: Math.min(totalPaginas, 5) }, (_, i) => {
          let p = i + 1
          if (totalPaginas > 5 && pagina > 3) p = pagina - 2 + i
          if (p > totalPaginas) return null
          return (
            <button
              key={p}
              onClick={() => onChange(p)}
              className={`w-8 h-8 rounded-lg text-xs font-medium transition-colors ${
                p === pagina
                  ? 'bg-volt-400/20 text-volt-300 border border-volt-400/30'
                  : 'text-ink-400 hover:text-white hover:bg-ink-700'
              }`}
            >
              {p}
            </button>
          )
        })}
        <button
          onClick={() => onChange(pagina + 1)}
          disabled={pagina === totalPaginas}
          className="px-3 py-1.5 rounded-lg text-xs text-ink-300 hover:text-white hover:bg-ink-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          Próxima →
        </button>
      </div>
    </div>
  )
}
