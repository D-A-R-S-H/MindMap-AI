import useFetch from "../hooks/useFetch";
import { getTeacherAnalytics } from "../api/client";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import ErrorMessage from "../components/ui/ErrorMessage";
import MasteryBarChart from "../components/charts/MasteryBarChart";

export default function Teacher() {
  const { data, loading, error } = useFetch(getTeacherAnalytics);
  if (loading) return <Spinner label="Loading class analytics..." />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-[#0f1b4d]">Teacher dashboard</h2>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <p className="text-sm text-slate-500">Class average mastery</p>
          <p className="mt-1 text-3xl font-bold text-[#0f1b4d]">{data.class_avg_mastery}%</p>
        </Card>
        <Card>
          <p className="text-sm text-slate-500">Topics needing extra teaching</p>
          <p className="mt-1 font-semibold text-red-700">{data.needs_teaching.join(", ") || "None"}</p>
        </Card>
      </div>

      <Card>
        <h3 className="mb-2 font-semibold text-[#0f1b4d]">Concept difficulty (class average mastery)</h3>
        <MasteryBarChart data={data.concepts} xKey="name" yKey="avg_mastery" />
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h3 className="mb-3 font-semibold text-[#0f1b4d]">Common misconceptions</h3>
          <ul className="space-y-2 text-sm">
            {data.common_misconceptions.map((m, i) => (
              <li key={i} className="flex justify-between gap-3">
                <span className="text-slate-700">{m.text}</span>
                <span className="font-semibold text-red-600">{m.count} students</span>
              </li>
            ))}
          </ul>
        </Card>
        <Card>
          <h3 className="mb-3 font-semibold text-[#0f1b4d]">Student performance</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500">
                <th className="pb-2">Student</th><th>Avg mastery</th><th>Weakest concept</th>
              </tr>
            </thead>
            <tbody>
              {data.students.map((s) => (
                <tr key={s.name} className="border-t border-slate-100">
                  <td className="py-2 font-medium">{s.name}</td>
                  <td>{s.avg_mastery}%</td>
                  <td>{s.weakest_concept}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  );
}