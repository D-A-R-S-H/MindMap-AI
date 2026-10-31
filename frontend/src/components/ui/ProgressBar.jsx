export default function ProgressBar({ value, color = "bg-indigo-600" }) {
  return (
    <div className="h-2.5 w-full rounded-full bg-slate-200">
      <div className={`h-2.5 rounded-full ${color} transition-all`} style={{ width: `${Math.min(100, value)}%` }} />
    </div>
  );
}