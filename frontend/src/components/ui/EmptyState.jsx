export default function EmptyState({ title, text }) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-300 p-10 text-center">
      <p className="font-semibold text-[#0f1b4d]">{title}</p>
      <p className="mt-1 text-sm text-slate-500">{text}</p>
    </div>
  );
}