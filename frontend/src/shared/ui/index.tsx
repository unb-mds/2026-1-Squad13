import type { ReactNode, ButtonHTMLAttributes, InputHTMLAttributes, SelectHTMLAttributes } from 'react'
import { Loader2, TrendingUp, TrendingDown, Info, type LucideIcon } from 'lucide-react'

// --- Card ---
export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`bg-card border border-border rounded-xl ${className}`}>{children}</div>
  )
}

export function CardHeader({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`px-5 py-4 border-b border-border ${className}`}>{children}</div>
}

export function CardBody({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`px-5 py-4 ${className}`}>{children}</div>
}

// --- Badge ---
type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'volt'
const badgeClasses: Record<BadgeVariant, string> = {
  default: 'bg-muted text-muted-foreground border-border',
  success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25',
  warning: 'bg-amber-500/15 text-amber-400 border-amber-500/25',
  danger: 'bg-rose-500/15 text-rose-400 border-rose-500/25',
  info: 'bg-blue-500/15 text-blue-400 border-blue-500/25',
  volt: 'bg-primary/15 text-primary border-primary/25',
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
  primary: 'bg-primary text-primary-foreground hover:bg-primary/90 font-semibold',
  secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 border border-border',
  ghost: 'text-muted-foreground hover:text-foreground hover:bg-secondary/60',
  danger: 'bg-destructive/15 text-destructive hover:bg-destructive/25 border border-destructive/25',
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
      {label && <label className="block text-sm text-muted-foreground mb-1.5 font-medium">{label}</label>}
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">{leftIcon}</div>
        )}
        <input
          className={`w-full bg-input-background border border-border text-foreground placeholder-muted-foreground rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all ${leftIcon ? 'pl-9' : ''} ${error ? 'border-destructive/50' : ''} ${className}`}
          {...props}
        />
      </div>
      {error && <p className="mt-1.5 text-xs text-destructive">{error}</p>}
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
      {label && <label className="block text-sm text-muted-foreground mb-1.5 font-medium">{label}</label>}
      <select
        className={`w-full bg-input-background border border-border text-foreground rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all appearance-none ${className}`}
        {...props}
      >
        {children}
      </select>
    </div>
  )
}

// --- Spinner ---
export function Spinner({ className = '' }: { className?: string }) {
  return <Loader2 role="status" aria-label="Carregando" className={`animate-spin text-primary ${className}`} />
}

// --- Empty State ---
export function EmptyState({ title, description, icon }: { title: string; description?: string; icon?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && <div className="mb-4 text-muted-foreground">{icon}</div>}
      <p className="text-foreground font-medium">{title}</p>
      {description && <p className="mt-1 text-sm text-muted-foreground max-w-sm">{description}</p>}
    </div>
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
      <p className="text-xs text-muted-foreground">
        Exibindo <span className="text-foreground">{inicio}–{fim}</span> de <span className="text-foreground">{total}</span>
      </p>
      <div className="flex gap-1">
        <button
          onClick={() => onChange(pagina - 1)}
          disabled={pagina === 1}
          className="px-3 py-1.5 rounded-lg text-xs text-muted-foreground hover:text-foreground hover:bg-secondary disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
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
                  ? 'bg-primary/20 text-primary border border-primary/30'
                  : 'text-muted-foreground hover:text-foreground hover:bg-secondary'
              }`}
            >
              {p}
            </button>
          )
        })}
        <button
          onClick={() => onChange(pagina + 1)}
          disabled={pagina === totalPaginas}
          className="px-3 py-1.5 rounded-lg text-xs text-muted-foreground hover:text-foreground hover:bg-secondary disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          Próxima →
        </button>
      </div>
    </div>
  )
}

// --- KpiCard ---
interface KpiCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: LucideIcon
  trend?: {
    value: string
    isPositive: boolean
  }
  isAlarm?: boolean
  metadata?: {
    definition: string
    source: string
    rule: string
  }
}

export function KpiCard({ title, value, subtitle, icon: Icon, trend, isAlarm, metadata }: KpiCardProps) {
  return (
    <div
      className={`bg-card border rounded-lg p-6 transition-all ${
        isAlarm
          ? "border-l-4 border-l-destructive hover:bg-destructive/5 hover:shadow-lg"
          : "border-border hover:shadow-md"
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-1.5 mb-1 relative group">
            <p className="text-sm text-muted-foreground">{title}</p>
            {metadata && (
              <div className="inline-block relative">
                <Info className="w-3.5 h-3.5 text-muted-foreground/50 hover:text-foreground cursor-pointer transition-colors" />
                <div className="invisible opacity-0 group-hover:visible group-hover:opacity-100 absolute left-0 bottom-6 z-50 w-64 p-3 bg-card border border-border rounded-lg shadow-xl text-xs text-foreground transition-all duration-200 pointer-events-none">
                  <div className="space-y-2">
                    <div>
                      <span className="font-semibold text-primary block mb-0.5">Definição</span>
                      <span className="text-muted-foreground">{metadata.definition}</span>
                    </div>
                    <div>
                      <span className="font-semibold text-primary block mb-0.5">Regra de Cálculo</span>
                      <span className="text-muted-foreground">{metadata.rule}</span>
                    </div>
                    <div>
                      <span className="font-semibold text-primary block mb-0.5">Fonte</span>
                      <span className="text-muted-foreground">{metadata.source}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
          <div className="flex items-baseline gap-2">
            <h3
              className={`font-semibold ${
                isAlarm ? "text-4xl text-destructive" : "text-3xl text-foreground"
              }`}
            >
              {value}
            </h3>
          </div>
          {subtitle && (
            <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className="flex items-center gap-1.5 mt-2">
              {trend.isPositive ? (
                <TrendingUp className="w-3.5 h-3.5 text-success" />
              ) : (
                <TrendingDown className="w-3.5 h-3.5 text-destructive" />
              )}
              <span
                className={`text-xs font-medium ${
                  trend.isPositive ? "text-success-foreground" : "text-destructive-foreground"
                }`}
              >
                {trend.value}
              </span>
            </div>
          )}
        </div>
        <div
          className={`flex items-center justify-center w-12 h-12 rounded-lg ${
            isAlarm ? "bg-destructive/10" : "bg-primary/10"
          }`}
        >
          <Icon className={`w-6 h-6 ${isAlarm ? "text-destructive" : "text-primary"}`} />
        </div>
      </div>
    </div>
  )
}


