export default function MilestoneItem({ milestone, isLast }) {
  return (
    <div className="flex gap-4">
      {/* Timeline spine */}
      <div className="flex flex-col items-center">
        <div className="w-10 h-10 rounded-full bg-blue-500/20 border-2 border-blue-500 flex items-center justify-center text-sm font-bold text-blue-300 shrink-0">
          W{milestone.week}
        </div>
        {!isLast && <div className="w-0.5 flex-1 bg-slate-700 mt-1" />}
      </div>

      {/* Content */}
      <div className={`pb-8 ${isLast ? '' : ''}`}>
        <p className="text-white font-medium mb-2 leading-relaxed">
          {milestone.checkpoint}
        </p>
        <div className="flex flex-wrap gap-1.5">
          {(milestone.skills_unlocked || []).map((s) => (
            <span
              key={s}
              className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/20"
            >
              ✓ {s}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
