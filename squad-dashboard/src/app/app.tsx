import { Routes, Route } from 'react-router-dom'
import { Sidebar } from '@/widgets/sidebar'
import { DashboardPage } from '@/pages/dashboard-page'
import { BoardPage } from '@/pages/board-page'
import { FeaturesPage } from '@/pages/features-page'
import { TeamPage } from '@/pages/team-page'
import { RoadmapPage } from '@/pages/roadmap-page'

export function App() {
  return (
    <div className="min-h-screen bg-surface-0 text-slate-100 font-sans">
      <Sidebar />
      <main className="ml-0 md:ml-56 px-4 md:px-6 pt-16 md:pt-6 pb-20 md:pb-6 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/board" element={<BoardPage />} />
            <Route path="/features" element={<FeaturesPage />} />
            <Route path="/team" element={<TeamPage />} />
            <Route path="/roadmap" element={<RoadmapPage />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}
