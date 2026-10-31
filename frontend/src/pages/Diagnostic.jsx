import { useState } from "react";
import { Link } from "react-router-dom";
import useFetch from "../hooks/useFetch";
import { getQuestions, submitDiagnostic } from "../api/client";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import ErrorMessage from "../components/ui/ErrorMessage";
import ProgressBar from "../components/ui/ProgressBar";
import Badge from "../components/ui/Badge";

export default function Diagnostic() {
  const { data: questions, loading, error } = useFetch(() => getQuestions({ type: "diagnostic" }));
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [profile, setProfile] = useState(null);
  const [submitError, setSubmitError] = useState(null);

  if (loading) return <Spinner label="Loading diagnostic..." />;
  if (error) return <ErrorMessage message={error} />;
  if (!questions?.length) return <p>No diagnostic questions available.</p>;

  if (submitting) return <Spinner label="Building your learner profile..." />;

  if (profile) {
    return (
      <div className="max-w-3xl mx-auto space-y-5">
        <h2 className="text-2xl font-bold text-[#0f1b4d]">Your learner profile</h2>
        <Card className="space-y-3">
          {profile.profile.map((p) => (
            <div key={p.concept_id}>
              <div className="mb-1 flex justify-between text-sm">
                <span className="font-medium text-slate-700">{p.concept_name}</span>
                <span className="flex items-center gap-2">
                  {p.mastery}% <Badge tone={p.level}>{p.level}</Badge>
                </span>
              </div>
              <ProgressBar value={p.mastery} />
            </div>
          ))}
        </Card>
        <div className="flex gap-3">
          <Link to="/recall" className="rounded-xl bg-indigo-600 px-5 py-2.5 font-medium text-white hover:bg-indigo-700">
            Practise with Speak & Recall
          </Link>
          <Link to="/dashboard" className="rounded-xl border border-slate-300 px-5 py-2.5 font-medium text-slate-700 hover:bg-white">
            Go to dashboard
          </Link>
        </div>
      </div>
    );
  }

  const q = questions[index];
  const isLast = index === questions.length - 1;
  const value = answers[q.id] || "";

  const finish = async () => {
    setSubmitting(true);
    setSubmitError(null);
    try {
      const payload = questions.map((x) => ({ question_id: x.id, answer_text: answers[x.id] || "" }));
      setProfile(await submitDiagnostic(payload));
    } catch {
      setSubmitError("Could not submit the diagnostic. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      <h2 className="text-2xl font-bold text-[#0f1b4d]">Diagnostic assessment</h2>
      <div>
        <p className="mb-1 text-sm text-slate-500">Question {index + 1} of {questions.length}</p>
        <ProgressBar value={((index + 1) / questions.length) * 100} />
      </div>
      <Card>
        <span className="text-xs font-semibold uppercase tracking-wide text-indigo-600">{q.concept_name}</span>
        <p className="mt-2 text-xl font-semibold text-[#0f1b4d]">{q.question_text}</p>
        <textarea
          value={value}
          onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
          placeholder="Type or dictate your answer with Wispr Flow..."
          className="mt-4 w-full min-h-[160px] rounded-xl border border-slate-200 p-4 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
        {submitError && <p className="mt-2 text-sm text-red-600">{submitError}</p>}
        <div className="mt-4 flex justify-between">
          <button
            onClick={() => setIndex(index - 1)}
            disabled={index === 0}
            className="rounded-xl border border-slate-300 px-5 py-2.5 text-slate-700 disabled:opacity-40"
          >
            Back
          </button>
          {isLast ? (
            <button onClick={finish} className="rounded-xl bg-indigo-600 px-6 py-2.5 font-medium text-white hover:bg-indigo-700">
              Finish & see profile
            </button>
          ) : (
            <button onClick={() => setIndex(index + 1)} className="rounded-xl bg-indigo-600 px-6 py-2.5 font-medium text-white hover:bg-indigo-700">
              Next
            </button>
          )}
        </div>
      </Card>
    </div>
  );
}