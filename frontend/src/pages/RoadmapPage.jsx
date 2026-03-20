import { useState } from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import { getInterviewPrep } from '../api';
import CourseCard from '../components/CourseCard';
import MilestoneItem from '../components/MilestoneItem';
import FallbackBanner from '../components/FallbackBanner';
import LoadingSpinner from '../components/LoadingSpinner';

const confBadge = {
  high: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  medium: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  low: 'bg-red-500/15 text-red-300 border-red-500/30',
};

export default function RoadmapPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state;
  const [loadingPrep, setLoadingPrep] = useState(false);
  const [prepError, setPrepError] = useState(null);

  if (!state?.roadmap) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <p className="text-slate-400 mb-4">No roadmap data found.</p>
        <Link to="/analyze" className="text-blue-400 hover:text-blue-300 underline">← Start a new analysis</Link>
      </div>
    );
  }

  const { roadmap, profile, job } = state;
  const confKey = (roadmap.confidence_note || 'medium').split(' ')[0].split('—')[0].trim();
  const confCls = confBadge[confKey] || confBadge.medium;

  async function handleInterviewPrep() {
    setLoadingPrep(true);
    setPrepError(null);
    try {
      const prep = await getInterviewPrep(roadmap.profile_id, roadmap.job_id);
      navigate('/interview-prep', { state: { prep, profile, job } });
    } catch (e) {
      setPrepError(e.message);
      setLoadingPrep(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="mb-2">
        <Link to="/analyze" className="text-sm text-slate-500 hover:text-slate-300 transition-colors">← New analysis</Link>
      </div>

      <h1 className="text-3xl font-bold mb-1">Your Career Roadmap</h1>
      <p className="text-slate-400 mb-6">{profile?.name} → {job?.title}</p>

      {roadmap.fallback_used && <FallbackBanner />}

      {/* AI Narrative */}
      <div className="bg-slate-800/40 border-l-4 border-blue-500 rounded-r-xl p-6 mb-10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-blue-400">
            {roadmap.fallback_used ? '📋 Analysis Summary' : '🤖 AI Career Advisor'}
          </h2>
          <span className={`text-xs px-2 py-0.5 rounded-full border ${confCls}`}>
            confidence: {roadmap.confidence_note}
          </span>
        </div>
        <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">{roadmap.ai_narrative}</div>
      </div>

      {/* Courses */}
      {roadmap.recommended_courses?.length > 0 && (
        <section className="mb-12">
          <h2 className="text-xl font-bold mb-1">Recommended Courses</h2>
          <p className="text-slate-400 text-sm mb-6">{roadmap.recommended_courses.length} courses to close your skill gaps</p>
          <div className="grid md:grid-cols-2 gap-4">
            {roadmap.recommended_courses.map((c, i) => <CourseCard key={i} course={c} />)}
          </div>
        </section>
      )}

      {/* Milestones */}
      {roadmap.milestones?.length > 0 && (
        <section className="mb-12">
          <h2 className="text-xl font-bold mb-1">Learning Milestones</h2>
          <p className="text-slate-400 text-sm mb-6">Your week-by-week checkpoint plan</p>
          <div className="ml-2">
            {roadmap.milestones.map((m, i) => (
              <MilestoneItem key={i} milestone={m} isLast={i === roadmap.milestones.length - 1} />
            ))}
          </div>
        </section>
      )}

      {/* Bottom stat */}
      <div className="text-center py-8 bg-slate-800/30 rounded-xl border border-slate-700/40 mb-8">
        <p className="text-slate-400 text-sm mb-2">Estimated time to job-ready</p>
        <p className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
          {roadmap.estimated_weeks_to_ready} weeks
        </p>
        <p className="text-slate-500 text-xs mt-2">at 10–15 hours/week of focused study</p>
      </div>

      {/* Action buttons */}
      {prepError && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-red-300 text-sm mb-4 text-center">{prepError}</div>
      )}

      <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
        <button
          onClick={handleInterviewPrep}
          disabled={loadingPrep}
          className="px-8 py-3 rounded-xl font-semibold bg-purple-600 hover:bg-purple-500 text-white transition-all shadow-lg shadow-purple-600/25 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loadingPrep ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Generating Questions...
            </span>
          ) : '🎯 Practice Interview Questions'}
        </button>
        <Link to="/analyze" className="px-8 py-3 rounded-xl font-semibold bg-slate-700 hover:bg-slate-600 text-white transition-all">
          ← Analyze Another Role
        </Link>
      </div>
    </div>
  );
}
