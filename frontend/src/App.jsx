import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AnalyzePage from './pages/AnalyzePage';
import ResultsPage from './pages/ResultsPage';
import RoadmapPage from './pages/RoadmapPage';
import InterviewPrepPage from './pages/InterviewPrepPage';
import HealthBadge from './components/HealthBadge';

function Navbar() {
  const location = useLocation();
  const isHome = location.pathname === '/';

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isHome ? 'bg-transparent' : 'bg-slate-900/90 backdrop-blur-md border-b border-slate-700/50'}`}>
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <span className="text-2xl">🌉</span>
          <span className="text-lg font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent group-hover:from-blue-300 group-hover:to-cyan-200 transition-all">
            SkillBridge
          </span>
        </Link>
        <div className="flex items-center gap-6">
          <Link to="/analyze" className="text-sm text-slate-300 hover:text-white transition-colors">
            Analyze
          </Link>
          <HealthBadge />
        </div>
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main className="pt-16">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analyze" element={<AnalyzePage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/roadmap" element={<RoadmapPage />} />
          <Route path="/interview-prep" element={<InterviewPrepPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
