import { useState, useEffect } from 'react';
import { fetchHealth } from '../api';

const statusConfig = {
  up: { color: 'bg-emerald-400', label: 'AI Online', ring: 'ring-emerald-400/30' },
  degraded: { color: 'bg-amber-400', label: 'AI Slow', ring: 'ring-amber-400/30' },
  down: { color: 'bg-red-400', label: 'AI Offline', ring: 'ring-red-400/30' },
};

export default function HealthBadge() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    let mounted = true;

    async function check() {
      try {
        const data = await fetchHealth();
        if (mounted) setHealth(data);
      } catch {
        if (mounted) setHealth({ status: 'down' });
      }
    }

    check();
    const interval = setInterval(check, 30000);
    return () => { mounted = false; clearInterval(interval); };
  }, []);

  const cfg = statusConfig[health?.status] || statusConfig.down;

  return (
    <div className="flex items-center gap-2 text-xs text-slate-400">
      <div className={`relative w-2.5 h-2.5 rounded-full ${cfg.color}`}>
        <div className={`absolute inset-0 rounded-full ${cfg.color} animate-ping opacity-40`} />
      </div>
      <span>{cfg.label}</span>
      {health?.latency_ms != null && (
        <span className="text-slate-500">{health.latency_ms}ms</span>
      )}
    </div>
  );
}
