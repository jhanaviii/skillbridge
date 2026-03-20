export default function LoadingSpinner({ message = 'Analyzing...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin" />
      <p className="text-slate-400 text-sm animate-pulse">{message}</p>
    </div>
  );
}
