export default function FallbackBanner() {
  return (
    <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg px-4 py-3 flex items-center gap-3 mb-6">
      <span className="text-amber-400 text-lg">⚠️</span>
      <div>
        <p className="text-amber-200 text-sm font-medium">AI service unavailable — showing rule-based analysis</p>
        <p className="text-amber-200/60 text-xs mt-0.5">Results are computed using deterministic matching. Re-run when AI is back for enhanced insights.</p>
      </div>
    </div>
  );
}
