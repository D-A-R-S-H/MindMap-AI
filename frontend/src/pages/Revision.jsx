import { Link } from "react-router-dom";
import useFetch from "../hooks/useFetch";
import { getRevisions } from "../api/client";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import ErrorMessage from "../components/ui/ErrorMessage";
import EmptyState from "../components/ui/EmptyState";
import Badge from "../components/ui/Badge";

export default function Revision() {
  const { data, loading, error } = useFetch(getRevisions);
  if (loading) return <Spinner label="Loading revision plan..." />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      <h2 className="text-2xl font-bold text-[#0f1b4d]">Revision planner</h2>
      <p className="text-slate-500">Weak topics return tomorrow, developing in 3 days, strong in 7 days.</p>
      {data.length === 0 ? (
        <EmptyState title="No revisions scheduled" text="Answer a question in Speak & Recall to create your plan." />
      ) : (
        data.map((x) => (
          <Card key={x.concept_id} className="flex items-center justify-between">
            <div>
              <p className="font-semibold text-[#0f1b4d]">{x.concept_name}</p>
              <p className="text-sm text-slate-500">Due {x.due_date}</p>
            </div>
            <div className="flex items-center gap-3">
              <Badge tone={x.priority}>{x.priority}</Badge>
              <Link to="/recall" className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
                Revise
              </Link>
            </div>
          </Card>
        ))
      )}
    </div>
  );
}