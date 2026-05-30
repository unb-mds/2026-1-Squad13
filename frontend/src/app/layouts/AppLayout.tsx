import { Outlet, NavLink } from 'react-router-dom'
import { LayoutDashboard, FileText, BarChart3, Scale, ChevronRight, Bell } from 'lucide-react'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/proposicoes', icon: FileText, label: 'Proposições' },
  { to: '/relatorios', icon: BarChart3, label: 'Relatórios' },
]

export function AppLayout() {
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
