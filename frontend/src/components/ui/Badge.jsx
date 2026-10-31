const styles = {
  weak: "bg-red-100 text-red-700",
  developing: "bg-amber-100 text-amber-700",
  strong: "bg-green-100 text-green-700",
  high: "bg-red-100 text-red-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-green-100 text-green-700",
  default: "bg-indigo-100 text-indigo-700",
};

export default function Badge({ children, tone = "default" }) {
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${styles[tone] || styles.default}`}>
      {children}
    </span>
  );
}