import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, FileText, BarChart3, LogOut, Scale, ChevronRight, Bell } from 'lucide-react'
import { useAuth } from '../providers/AuthContext'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/proposicoes', icon: FileText, label: 'Proposições' },
  { to: '/relatorios', icon: BarChart3, label: 'Relatórios' },
]

export function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-ink-900 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 flex flex-col bg-ink-800 border-r border-ink-700/50 shrink-0">
        {/* Logo */}
        <div className="px-6 py-6 border-b border-ink-700/50">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-volt-400 rounded-lg flex items-center justify-center shrink-0">
              <Scale className="w-5 h-5 text-ink-900" />
            </div>
            <div>
              <p className="font-display font-700 text-white text-lg leading-none">LexTrack</p>
              <p className="text-ink-300 text-xs mt-0.5 font-mono">v1.0.0 — beta</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group ${
                  isActive
                    ? 'bg-volt-400/15 text-volt-300 border border-volt-400/25'
                    : 'text-ink-300 hover:text-white hover:bg-ink-700/60 border border-transparent'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="flex-1">{label}</span>
              <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-50 transition-opacity" />
            </NavLink>
          ))}
        </nav>

        {/* User */}
        <div className="px-3 py-4 border-t border-ink-700/50">
          <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg">
            <div className="w-8 h-8 rounded-full bg-volt-400/20 border border-volt-400/30 flex items-center justify-center shrink-0">
              <span className="text-volt-300 text-xs font-display font-700">
                {user?.nome?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-sm font-medium truncate">{user?.nome}</p>
              <p className="text-ink-400 text-xs truncate capitalize">{user?.perfil}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-1.5 rounded-md text-ink-400 hover:text-rose-400 hover:bg-rose-400/10 transition-colors"
              title="Sair"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <header className="h-14 bg-ink-800/50 border-b border-ink-700/50 flex items-center justify-end px-6 shrink-0">
          <button className="p-2 rounded-lg text-ink-400 hover:text-white hover:bg-ink-700/60 transition-colors">
            <Bell className="w-4 h-4" />
          </button>
        </header>

        {/* Page */}
        <div className="flex-1 overflow-y-auto">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
