import { useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { generateRoadmap } from '../api';
import CircularGauge from '../components/CircularGauge';
import SkillPill from '../components/SkillPill';
import FallbackBanner from '../components/FallbackBanner';
import LoadingSpinner from '../components/LoadingSpinner';

const fitConfig = {
  good_fit: { label: 'Good Fit', cls: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' },
  stretch: { label: 'Stretch Role', cls: 'bg-amber-500/15 text-amber-300 border-amber-500/30' },
  significant_gap: { label: 'Significant Gap', cls: 'bg-red-500/15 text-red-300 border-red-500/30' },
};

export default function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  const state = location.state;
  if (!state?.result) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <p className="text-slate-400 mb-4">No analysis results found.</p>
        <Link to="/analyze" className="text-blue-400 hover:text-blue-300 underline">
          ← Go back to analyze
        </Link>
      </div>
    );
  }

  const { result, profile, job } = state;
  const fit = fitConfig[result.seniority_fit] || fitConfig.significant_gap;

  // Build a lookup of priority by skill name for the missing skills column
  const priorityMap = {};
  (result.priority_order || []).forEach((p) => {
    priorityMap[p.skill] = p.priority;
  });

  async function handleRoadmap() {
    setGenerating(true);
    setError(null);
    try {
      const roadmap = await generateRoadmap(result.profile_id, result.job_id);
      navigate('/roadmap', {
        state: { roadmap, profile, job },
      });
    } catch (e) {
      setError(e.message);
      setGenerating(false);
    }
  }

  if (generating) return <LoadingSpinner message="Generating your personalized career roadmap..." />;

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      {/* Header */}
      <div className="mb-2">
        <Link to="/analyze" className="text-sm text-slate-500 hover:text-slate-300 transition-colors">
          ← Back to selection
        </Link>
      </div>
      <h1 className="text-3xl font-bold mb-1">Skill Gap Analysis</h1>
      <p className="text-slate-400 mb-6">
        {profile?.name} → {job?.title}
      </p>

      {result.fallback_used && <FallbackBanner />}

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-red-300 text-sm mb-6">
          {error}
        </div>
      )}

      {/* Top: Gauge + seniority fit */}
      <div className="flex flex-col md:flex-row items-center gap-8 mb-10">
        <CircularGauge percentage={result.match_percentage} />

        <div className="flex-1 space-y-3">
          <div>
            <span className="text-xs text-slate-500 block mb-1">Seniority Fit</span>
            <span className={`inline-block px-3 py-1 rounded-full border text-sm font-medium ${fit.cls}`}>
              {fit.label}
            </span>
          </div>
          <div>
            <span className="text-xs text-slate-500 block mb-1">Summary</span>
            <p className="text-slate-300 text-sm leading-relaxed">
              You match <strong className="text-white">{result.matched_skills.length}</strong> of{' '}
              <strong className="text-white">{result.matched_skills.length + result.missing_skills.length}</strong>{' '}
              total skills. {result.missing_skills.length === 0
                ? "You're fully qualified for this role!"
                : `${result.missing_skills.length} skills need development.`}
            </p>
          </div>
        </div>
      </div>

      {/* Skill columns */}
      <div className="grid md:grid-cols-2 gap-6 mb-10">
        {/* Matched */}
        <div className="bg-slate-800/40 border border-slate-700/40 rounded-xl p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-emerald-400 mb-4 flex items-center gap-2">
            <span>✓</span> You Have
            <span className="text-slate-500 font-normal">({result.matched_skills.length})</span>
          </h2>
          <div className="flex flex-wrap gap-2">
            {result.matched_skills.length === 0 ? (
              <p className="text-slate-500 text-sm italic">No matching skills found</p>
            ) : (
              result.matched_skills.map((s) => (
                <SkillPill key={s} skill={s} color="green" />
              ))
            )}
          </div>
        </div>

        {/* Missing */}
        <div className="bg-slate-800/40 border border-slate-700/40 rounded-xl p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-red-400 mb-4 flex items-center gap-2">
            <span>✗</span> You Need
            <span className="text-slate-500 font-normal">({result.missing_skills.length})</span>
          </h2>
          <div className="flex flex-wrap gap-2">
            {result.missing_skills.length === 0 ? (
              <p className="text-emerald-400 text-sm">🎉 No gaps — you have every skill!</p>
            ) : (
              result.missing_skills.map((s) => (
                <SkillPill key={s} skill={s} color="red" priority={priorityMap[s]} />
              ))
            )}
          </div>
        </div>
      </div>

      {/* Priority breakdown */}
      {result.priority_order?.length > 0 && (
        <div className="bg-slate-800/40 border border-slate-700/40 rounded-xl p-6 mb-10">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">
            Priority Breakdown
          </h2>
          <div className="space-y-3">
            {result.priority_order.map((p, i) => (
              <div key={i} className="flex items-start gap-3">
                <span className={`text-xs font-bold px-2 py-0.5 rounded shrink-0 mt-0.5 ${
                  p.priority === 'critical' ? 'bg-red-500 text-white' :
                  p.priority === 'important' ? 'bg-amber-500 text-black' :
                  'bg-slate-500 text-white'
                }`}>
                  {p.priority === 'nice_to_have' ? 'NICE' : p.priority.toUpperCase()}
                </span>
                <div>
                  <span className="text-white font-medium text-sm">{p.skill}</span>
                  {p.semantic_match_found && (
                    <span className="ml-2 text-xs text-cyan-400">🔗 semantic match found</span>
                  )}
                  <p className="text-slate-400 text-xs mt-0.5">{p.reason}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generate roadmap button */}
      <div className="text-center">
        <button
          onClick={handleRoadmap}
          className="px-10 py-3.5 rounded-xl font-semibold text-lg bg-blue-500 hover:bg-blue-400 text-white shadow-lg shadow-blue-500/25 hover:shadow-blue-400/30 hover:-translate-y-0.5 transition-all"
        >
          🗺️ Generate Career Roadmap
        </button>
      </div>
    </div>
  );
}
