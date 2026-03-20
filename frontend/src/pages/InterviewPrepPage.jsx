import { useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import FallbackBanner from '../components/FallbackBanner';

const diffConfig = {
  hard: { label: 'HARD', cls: 'bg-red-500 text-white', skillCls: 'bg-red-500/15 text-red-300 border-red-500/30' },
  medium: { label: 'MEDIUM', cls: 'bg-amber-500 text-black', skillCls: 'bg-amber-500/15 text-amber-300 border-amber-500/30' },
  easy: { label: 'EASY', cls: 'bg-emerald-500 text-white', skillCls: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' },
};

function QuestionCard({ question }) {
  const [open, setOpen] = useState(false);
  const cfg = diffConfig[question.difficulty] || diffConfig.medium;

  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5 hover:border-slate-600/70 transition-all">
      <div className="flex items-start justify-between gap-3 mb-3">
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${cfg.skillCls}`}>
          {question.skill}
        </span>
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded shrink-0 ${cfg.cls}`}>
          {cfg.label}
        </span>
      </div>

      <p className="text-white text-sm leading-relaxed mb-4">{question.question}</p>

      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-300 transition-colors"
      >
        <span>{open ? '▲' : '▼'}</span>
        <span>What interviewers look for</span>
      </button>

      {open && (
        <div className="mt-3 pt-3 border-t border-slate-700/50">
          <p className="text-xs text-slate-400 leading-relaxed">{question.what_to_look_for}</p>
        </div>
      )}
    </div>
  );
}

export default function InterviewPrepPage() {
  const location = useLocation();
  const state = location.state;

  if (!state?.prep) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <p className="text-slate-400 mb-4">No interview prep data found.</p>
        <Link to="/analyze" className="text-blue-400 hover:text-blue-300 underline">← Start a new analysis</Link>
      </div>
    );
  }

  const { prep, profile, job } = state;

  // Group questions by skill
  const grouped = {};
  for (const q of prep.questions) {
    if (!grouped[q.skill]) grouped[q.skill] = [];
    grouped[q.skill].push(q);
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="mb-2">
        <Link to="/analyze" className="text-sm text-slate-500 hover:text-slate-300 transition-colors">
          ← Back to analysis
        </Link>
      </div>

      <h1 className="text-3xl font-bold mb-1">Interview Prep</h1>
      <p className="text-slate-400 mb-6">
        {prep.questions.length} questions targeting skill gaps for {job?.title || 'your target role'}
      </p>

      {prep.fallback_used && <FallbackBanner />}

      {/* Questions by skill */}
      {Object.entries(grouped).map(([skill, questions]) => (
        <section key={skill} className="mb-8">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            {skill}
            <span className="text-xs text-slate-500 font-normal">({questions.length} question{questions.length > 1 ? 's' : ''})</span>
          </h2>
          <div className="space-y-4">
            {questions.map((q, i) => <QuestionCard key={i} question={q} />)}
          </div>
        </section>
      ))}

      {/* Summary */}
      <div className="text-center py-6 bg-slate-800/30 rounded-xl border border-slate-700/40 mt-8 mb-6">
        <p className="text-slate-400 text-sm">
          Practice these {prep.questions.length} questions to prepare for gaps in{' '}
          <span className="text-white font-medium">{Object.keys(grouped).join(', ')}</span>
        </p>
      </div>

      <div className="text-center">
        <Link to="/analyze" className="px-8 py-3 rounded-xl font-semibold bg-slate-700 hover:bg-slate-600 text-white transition-all">
          ← Analyze Another Role
        </Link>
      </div>
    </div>
  );
}
