import { useState } from "react";
import { Eye, EyeOff, Mic } from "lucide-react";
import useFetch from "../hooks/useFetch";
import { getQuestions, evaluateAnswer } from "../api/client";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import EvaluationResult from "../components/recall/EvaluationResult";

export default function SpeakRecall() {
  const { data: questions, loading, error } = useFetch(() => getQuestions());
  const [current, setCurrent] = useState(null);
  const [showRef, setShowRef] = useState(false);
  const [answer, setAnswer] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [submitError, setSubmitError] = useState(null);

  if (loading) return <Spinner label="Loading questions..." />;
  if (error) return <p className="text-red-600">Could not load questions: {error}</p>;

  const q = current || questions?.[0];
  if (!q) return <p>No questions available.</p>;

  const submit = async () => {
    setSubmitting(true);
    setSubmitError(null);
    try {
      setResult(await evaluateAnswer(q.id, answer));
    } catch (e) {
      setSubmitError("Evaluation failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const goNext = () => {
    const nq = result.next_question;
    setCurrent(questions.find((x) => x.id === nq.id) || { ...nq, expected_answer: "" });
    setAnswer("");
    setResult(null);
    setShowRef(false);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      <h2 className="text-2xl font-bold text-[#0f1b4d]">Speak & Recall</h2>

      <Card>
        <span className="text-xs font-semibold uppercase tracking-wide text-indigo-600">{q.concept_name}</span>
        <p className="mt-2 text-xl font-semibold text-[#0f1b4d]">{q.question_text}</p>

        {q.expected_answer && (
          <>
            <button
              onClick={() => setShowRef(!showRef)}
              className="mt-4 flex items-center gap-2 text-sm text-slate-600 hover:text-indigo-600"
            >
              {showRef ? <EyeOff size={16} /> : <Eye size={16} />}
              {showRef ? "Hide reference answer" : "Show reference answer"}
            </button>
            {showRef && (
              <p className="mt-2 rounded-xl bg-slate-50 p-4 text-sm text-slate-700">{q.expected_answer}</p>
            )}
          </>
        )}
      </Card>

      {!result && (
        <Card>
          <label className="flex items-center gap-2 font-medium text-slate-700 mb-2">
            <Mic size={18} className="text-indigo-600" /> Your answer
          </label>
          <textarea
            autoFocus
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Click here and dictate your answer with Wispr Flow. Explain it in your own words."
            className="w-full min-h-[220px] rounded-xl border border-slate-200 p-4 text-lg leading-relaxed focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          {submitError && <p className="mt-2 text-sm text-red-600">{submitError}</p>}
          <div className="mt-4 flex items-center gap-4">
            <button
              onClick={submit}
              disabled={submitting || answer.trim().length < 3}
              className="rounded-xl bg-indigo-600 px-6 py-3 font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              Submit answer
            </button>
            {submitting && <Spinner label="Analysing your understanding..." />}
          </div>
        </Card>
      )}

      {result && <EvaluationResult result={result} onNext={goNext} />}
    </div>
  );
}