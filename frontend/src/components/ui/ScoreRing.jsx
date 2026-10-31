export default function ScoreRing({ value, label, color = "#4f46e5" }) {
  const r = 42;
  const c = 2 * Math.PI * r;
  return (
    <div className="flex flex-col items-center">
      <svg width="110" height="110" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke="#e2e8f0" strokeWidth="9" />
        <circle
          cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="9"
          strokeLinecap="round" strokeDasharray={c}
          strokeDashoffset={c - (value / 100) * c}
          transform="rotate(-90 50 50)"
        />
        <text x="50" y="56" textAnchor="middle" className="fill-[#0f1b4d] text-xl font-bold">{value}</text>
      </svg>
      <span className="text-sm text-slate-600 mt-1">{label}</span>
    </div>
  );
}