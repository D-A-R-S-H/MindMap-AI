import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function MasteryBarChart({ data, xKey = "concept_name", yKey = "mastery" }) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <BarChart data={data} margin={{ bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey={xKey} interval={0} angle={-30} textAnchor="end" tick={{ fontSize: 11 }} />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Bar dataKey={yKey} fill="#4f46e5" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}