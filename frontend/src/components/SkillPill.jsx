const colorMap = {
  green: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  red: 'bg-red-500/15 text-red-300 border-red-500/30',
  blue: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  gray: 'bg-slate-600/30 text-slate-300 border-slate-500/30',
};

const priorityBadge = {
  critical: { label: 'CRITICAL', cls: 'bg-red-500 text-white' },
  important: { label: 'IMPORTANT', cls: 'bg-amber-500 text-black' },
  nice_to_have: { label: 'NICE TO HAVE', cls: 'bg-slate-500 text-white' },
};

export default function SkillPill({ skill, color = 'gray', priority }) {
  const badge = priority ? priorityBadge[priority] : null;

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm border ${colorMap[color] || colorMap.gray}`}>
      {skill}
      {badge && (
        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${badge.cls}`}>
          {badge.label}
        </span>
      )}
    </span>
  );
}
