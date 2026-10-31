import useFetch from "../hooks/useFetch";
import { getMastery } from "../api/client";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import ErrorMessage from "../components/ui/ErrorMessage";
import ProgressBar from "../components/ui/ProgressBar";
import Badge from "../components/ui/Badge";
import MasteryRadarChart from "../components/charts/MasteryRadarChart";

const barColor = { weak: "bg-red-500", developing: "bg-amber-500", strong: "bg-green-500" };

export default function Mastery() {
  const { data, loading, error } = useFetch(getMastery);
  if (loading) return <Spinner label="Loading mastery..." />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-[#0f1b4d]">Topic mastery</h2>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card><MasteryRadarChart data={data} /></Card>
        <Card className="space-y-4">
          {data.map((c) => (
            <div key={c.concept_id}>
              <div className="mb-1 flex justify-between text-sm">
                <span className="font-medium text-slate-700">{c.concept_name}</span>
                <span className="flex items-center gap-2">
                  {c.mastery}% <Badge tone={c.level}>{c.level}</Badge>
                </span>
              </div>
              <ProgressBar value={c.mastery} color={barColor[c.level]} />
              <p className="mt-1 text-xs text-slate-400">{c.attempts} attempts</p>
            </div>
          ))}
        </Card>
      </div>
    </div>
  );
}