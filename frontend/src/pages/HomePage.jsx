import { Link } from 'react-router-dom';

const steps = [
  { icon: '👤', title: 'Select Profile', desc: 'Choose from pre-loaded candidate profiles or create your own' },
  { icon: '🔍', title: 'Analyze Gap', desc: 'AI compares your skills against real job requirements' },
  { icon: '🗺️', title: 'Get Roadmap', desc: 'Receive a personalized learning plan with courses and milestones' },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-blue-950/40 to-slate-900">
      {/* Hero */}
      <section className="max-w-4xl mx-auto px-4 pt-32 pb-20 text-center">
        <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-300 text-sm">
          ✨ AI-Powered Career Intelligence
        </div>

        <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
          <span className="bg-gradient-to-r from-white via-blue-100 to-blue-200 bg-clip-text text-transparent">
            Find Your Path to
          </span>
          <br />
          <span className="bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
            Your Dream Role
          </span>
        </h1>

        <p className="text-lg text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          AI-powered skill gap analysis and personalized learning roadmaps.
          See exactly what you need to learn, how long it will take, and the
          best resources to get there.
        </p>

        <Link
          to="/analyze"
          className="inline-flex items-center gap-2 px-8 py-3.5 bg-blue-500 hover:bg-blue-400 text-white font-semibold rounded-xl transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-400/30 hover:-translate-y-0.5"
        >
          Get Started
          <span className="text-lg">→</span>
        </Link>
      </section>

      {/* How it works */}
      <section className="max-w-4xl mx-auto px-4 pb-32">
        <h2 className="text-center text-sm font-semibold uppercase tracking-widest text-slate-500 mb-10">
          How it works
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {steps.map((step, i) => (
            <div
              key={i}
              className="bg-slate-800/40 border border-slate-700/40 rounded-xl p-6 text-center hover:border-blue-500/30 transition-all"
            >
              <div className="text-4xl mb-4">{step.icon}</div>
              <div className="text-xs font-bold text-blue-400 mb-2">STEP {i + 1}</div>
              <h3 className="text-white font-semibold mb-2">{step.title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
