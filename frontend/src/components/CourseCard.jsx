export default function CourseCard({ course }) {
  const isFree = course.cost === 'free';

  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5 hover:border-blue-500/30 transition-all group">
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">
          {course.skill}
        </span>
        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${isFree ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-600/40 text-slate-400'}`}>
          {isFree ? '✦ FREE' : 'PAID'}
        </span>
      </div>

      <h3 className="text-white font-semibold mb-1 group-hover:text-blue-300 transition-colors">
        {course.course_name}
      </h3>

      <p className="text-slate-400 text-sm mb-3">{course.provider}</p>

      <p className="text-slate-500 text-xs mb-4 leading-relaxed">{course.reason}</p>

      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-500">
          ⏱ {course.estimated_hours}h estimated
        </span>
        <a
          href={course.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs font-medium px-3 py-1.5 rounded-lg bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 transition-colors"
        >
          View Course →
        </a>
      </div>
    </div>
  );
}
