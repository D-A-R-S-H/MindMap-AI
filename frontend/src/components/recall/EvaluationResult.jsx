import Card from "../ui/Card";
import ScoreRing from "../ui/ScoreRing";

function PointList({ title, items, tone }) {
  if (!items?.length) return null;
  return (
    <div>
      <h4 className={`font-semibold mb-2 ${tone}`}>{title}</h4>
      <ul className="list-disc pl-5 space-y-1 text-sm text-slate-700">
        {items.map((p, i) => <li key={i}>{p}</li>)}
      </ul>
    </div>
  );
}

export default function EvaluationResult({ result, onNext }) {
  const m = result.updated_mastery;
  return (
    <div className="space-y-5">
      {result.is_fallback && (
        <div className="rounded-xl bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 text-sm">
          ⚠️ Demo fallback evaluation. The Gemini AI was not used for this result.
        </div>
      )}

      <Card className="flex justify-around">
        <ScoreRing value={result.recall_score} label="Recall" />
        <ScoreRing value={result.understanding_score} label="Understanding" color="#7c3aed" />
      </Card>

      <Card className="space-y-5">
        <PointList title="✅ What you got right" items={result.correct_points} tone="text-green-700" />
        <PointList title="🧩 What you missed" items={result.missing_points} tone="text-amber-700" />
        <PointList title="❌ Incorrect statements" items={result.incorrect_points} tone="text-red-700" />
        <PointList title="⚠️ Misconceptions" items={result.misconceptions} tone="text-red-700" />
        <PointList title="💡 How to improve" items={result.improvement_suggestions} tone="text-indigo-700" />
        {result.follow_up_question && (
          <div className="rounded-xl bg-indigo-50 p-4 text-sm text-indigo-900">
            <b>Think about this:</b> {result.follow_up_question}
          </div>
        )}
      </Card>

      <Card className="text-sm text-slate-700 space-y-2">
        <p>
          <b>{m.concept_name}</b> mastery: {m.old}% → <b className="text-indigo-600">{m.new}%</b>
        </p>
        <p>Revise again on: <b>{result.next_revision_date}</b></p>
        {result.next_question && (
          <button
            onClick={onNext}
            className="mt-3 rounded-xl bg-indigo-600 px-5 py-2.5 font-medium text-white hover:bg-indigo-700"
          >
            Next question: {result.next_question.concept_name} →
          </button>
        )}
      </Card>
    </div>
  );
}