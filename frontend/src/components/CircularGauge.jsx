export default function CircularGauge({ percentage = 0, size = 180 }) {
  const pct = Math.min(100, Math.max(0, percentage));
  const color = pct < 40 ? '#ef4444' : pct < 70 ? '#eab308' : '#22c55e';
  const trackColor = '#1e293b';

  const gaugeStyle = {
    width: size,
    height: size,
    borderRadius: '50%',
    background: `conic-gradient(${color} ${pct * 3.6}deg, ${trackColor} ${pct * 3.6}deg)`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  };

  const innerStyle = {
    width: size - 24,
    height: size - 24,
    borderRadius: '50%',
    backgroundColor: '#0f172a',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  };

  return (
    <div style={gaugeStyle}>
      <div style={innerStyle}>
        <span className="text-4xl font-bold" style={{ color }}>
          {pct.toFixed(0)}%
        </span>
        <span className="text-xs text-slate-400 mt-1">skill match</span>
      </div>
    </div>
  );
}
