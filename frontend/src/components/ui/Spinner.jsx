export default function Spinner({ label = "Loading..." }) {
  return (
    <div className="flex items-center gap-3 text-indigo-600">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />
      <span className="text-sm font-medium">{label}</span>
    </div>
  );
}