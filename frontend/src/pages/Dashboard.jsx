import { Link } from "react-router-dom";
import useFetch from "../hooks/useFetch";
import { getProgress, getMastery, getRevisions } from "../api/client";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import ErrorMessage from "../components/ui/ErrorMessage";
import EmptyState from "../components/ui/EmptyState";
import ProgressBar from "../components/ui/ProgressBar";
import Badge from "../components/ui/Badge";
import MasteryBarChart from "../components/charts/MasteryBarChart";
import MasteryRadarChart from "../components/charts/MasteryRadarChart";

function Stat({ label, value }) {
  return (
    <Card>
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-3xl font-bold text-[#0f1b4d]">{value}</p>
    </Card>
  );
}

export default function Dashboard() {
  const p = useFetch(getProgress);
  const m = useFetch(getMastery);
  const r = useFetch(getRevisions);

  if (p.loading || m.loading || r.loading) return <Spinner label="Loading your dashboard..." />;
  const err = p.error || m.error || r.error;
  if (err) return <ErrorMessage message={err} />;

  const prog = p.data;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[#0f1b4d]">Welcome back, {prog.name} 👋</h2>
        <p className="text-slate-500">Don't just learn the answer. Understand what you don't understand.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Overall progress" value={`${prog.overall_progress}%`} />
        <Stat label="Questions attempted" value={prog.questions_attempted} />
        <Stat label="Avg recall" value={`${prog.avg_recall}%`} />
        <Stat label="Avg understanding" value={`${prog.avg_understanding}%`} />
      </div>

      <Card>
        <p className="mb-2 text-sm font-medium text-slate-600">Overall progress</p>
        <ProgressBar value={prog.overall_progress} />
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h3 className="mb-2 font-semibold text-[#0f1b4d]">Mastery by concept</h3>
          <MasteryBarChart data={m.data} />
        </Card>
        <Card>
          <h3 className="mb-2 font-semibold text-[#0f1b4d]">Concept map</h3>
          <MasteryRadarChart data={m.data} />
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h3 className="mb-3 font-semibold text-green-700">Strong concepts</h3>
          {prog.strong_concepts.length ? (
            <ul className="space-y-1 text-sm text-slate-700">
              {prog.strong_concepts.map((c) => <li key={c}>✅ {c}</li>)}
            </ul>
          ) : <p className="text-sm text-slate-500">None yet. Keep practising!</p>}
        </Card>
        <Card>
          <h3 className="mb-3 font-semibold text-red-700">Weak concepts</h3>
          {prog.weak_concepts.length ? (
            <ul className="space-y-1 text-sm text-slate-700">
              {prog.weak_concepts.map((c) => <li key={c}>⚠️ {c}</li>)}
            </ul>
          ) : <p className="text-sm text-slate-500">No weak concepts. Great work!</p>}
          <Link to="/recall" className="mt-4 inline-block rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
            Practise now
          </Link>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h3 className="mb-3 font-semibold text-[#0f1b4d]">Upcoming revision</h3>
          {r.data.length ? (
            <ul className="space-y-2 text-sm">
              {r.data.slice(0, 5).map((x) => (
                <li key={x.concept_id} className="flex items-center justify-between">
                  <span>{x.concept_name}</span>
                  <span className="flex items-center gap-2 text-slate-500">
                    {x.due_date} <Badge tone={x.priority}>{x.priority}</Badge>
                  </span>
                </li>
              ))}
            </ul>
          ) : <EmptyState title="Nothing due" text="Complete a Speak & Recall to schedule revision." />}
        </Card>
        <Card>
          <h3 className="mb-3 font-semibold text-[#0f1b4d]">Recent activity</h3>
          {prog.recent_activity.length ? (
            <ul className="space-y-3 text-sm">
              {prog.recent_activity.map((a, i) => (
                <li key={i}>
                  <p className="font-medium text-slate-700">{a.question}</p>
                  <p className="text-slate-500">
                    {a.concept} · Recall {a.recall}% · Understanding {a.understanding}%
                  </p>
                </li>
              ))}
            </ul>
          ) : <EmptyState title="No activity yet" text="Try your first Speak & Recall." />}
        </Card>
      </div>
    </div>
  );
}