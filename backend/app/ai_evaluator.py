import logging
import os
import re
import time

from .models import Question
from .schemas import AIEvaluation

log = logging.getLogger("mindmap.ai")

SYSTEM_PROMPT = """You are an expert Class 10 Physics teacher and a fair, encouraging evaluator.
A student has tried to recall an answer FROM MEMORY by speaking it (dictated with speech-to-text,
so expect informal wording, run-on sentences and small transcription errors).

You receive: the concept, the question, the reference answer, the key ideas a complete answer
should contain, and the student's response. Judge MEANING, not wording.

RULES
1. Never mark an idea wrong or missing just because the student used different words from the
   textbook. If the meaning matches a key idea, it counts as covered.
2. Ignore speech-to-text slips, filler words and grammar. Judge the physics.
3. recall_score (0-100): the share of the important key ideas the student actually conveyed.
4. understanding_score (0-100): whether the student shows WHY/HOW (reasoning, cause and effect,
   correct use of terms, ability to apply), not just repeated facts.
5. Choose exactly one answer_type:
   - "correct_reasoned": correct AND explains the reasoning
   - "paraphrased_correct": correct but expressed in clearly different words from the reference
   - "correct_shallow": correct statement but no reasoning/explanation
   - "partial": some key ideas right, important ones missing
   - "misconception": contains a wrong belief that shows a misunderstanding
6. correct_points: things the student said correctly. missing_points: important key ideas omitted.
   incorrect_points: statements that are factually wrong. misconceptions: the underlying
   misunderstanding behind wrong statements (empty list if none).
7. improvement_suggestions: 1-3 short, specific, kind tips on how to improve this answer.
8. If the answer is too short or vague to judge understanding (for example one phrase or a bare
   formula), do NOT guess. Give modest scores, and set follow_up_question to ONE short why/how
   question that would reveal their understanding. Otherwise set follow_up_question to null.
9. Never invent facts. Base everything on the question and the student's actual words.

Return ONLY a JSON object with exactly these keys, no markdown, no extra text:
{"recall_score": number, "understanding_score": number, "answer_type": string,
 "correct_points": [string], "missing_points": [string], "incorrect_points": [string],
 "misconceptions": [string], "improvement_suggestions": [string],
 "follow_up_question": string or null}"""


def _build_prompt(question: Question, concept_name: str, answer_text: str) -> str:
    return (
        f"Concept: {concept_name}\n"
        f"Question: {question.text}\n"
        f"Reference answer: {question.expected_answer}\n"
        f"Key ideas: {'; '.join(question.key_concepts or [])}\n\n"
        f"Student's dictated answer:\n\"\"\"\n{answer_text}\n\"\"\""
    )


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


TRANSIENT = ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500", "INTERNAL", "timed out", "timeout")


def _call_gemini(model: str, question: Question, concept_name: str, answer_text: str) -> AIEvaluation:
    from google import genai
    from google.genai import types

    timeout_ms = int(float(os.getenv("GEMINI_TIMEOUT_SECONDS", "10")) * 1000)
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"],
                          http_options=types.HttpOptions(timeout=timeout_ms))
    response = client.models.generate_content(
        model=model,
        contents=_build_prompt(question, concept_name, answer_text),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.2,
            max_output_tokens=900,  # the JSON answer is short; capping it keeps replies fast
        ),
    )
    result = AIEvaluation.model_validate_json(_strip_fences(response.text))
    result.is_fallback = False
    return result


def gemini_evaluate(question: Question, concept_name: str, answer_text: str) -> AIEvaluation:
    """Call Gemini with a hard time budget. Retries only briefly; raises if nothing succeeds in time."""
    budget = float(os.getenv("GEMINI_MAX_TOTAL_SECONDS", "15"))
    deadline = time.monotonic() + budget
    models = [os.getenv("GEMINI_MODEL", "gemini-3.8-flash")]
    models += [m.strip() for m in os.getenv("GEMINI_BACKUP_MODELS", "").split(",") if m.strip()]

    last_exc: Exception = TimeoutError("Gemini time budget used up")
    for model in models:
        for attempt in range(2):
            if time.monotonic() >= deadline:
                raise last_exc
            try:
                return _call_gemini(model, question, concept_name, answer_text)
            except Exception as exc:
                last_exc = exc
                log.warning("Gemini %s attempt %d failed: %s", model, attempt + 1, str(exc)[:200])
                if not any(t in str(exc) for t in TRANSIENT):
                    break  # permanent error: go straight to the next model
                time.sleep(0.5)
    raise last_exc


# ---------------------------------------------------------------- fallback
STOPWORDS = {
    "the", "and", "are", "for", "with", "from", "that", "this", "was",
    "has", "not", "its", "into", "than", "then", "also",
}
REASONING_WORDS = {"because", "so", "therefore", "since", "hence", "thus"}


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z]+", text.lower())


def _content_stems(text: str) -> set[str]:
    return {w[:5] for w in _words(text) if len(w) >= 3 and w not in STOPWORDS}


def _concept_covered(key_concept: str, answer_stems: set[str], answer_compact: str) -> bool:
    needed = _content_stems(key_concept)
    if not needed:
        return re.sub(r"\s+", "", key_concept.lower()) in answer_compact
    return len(needed & answer_stems) / len(needed) >= 0.5


def fallback_evaluate(question: Question, answer_text: str) -> AIEvaluation:
    """Keyword check used ONLY when Gemini is unavailable. It cannot judge understanding."""
    key_concepts = question.key_concepts or []
    answer_stems = _content_stems(answer_text)
    answer_compact = re.sub(r"\s+", "", answer_text.lower())

    covered = [k for k in key_concepts if _concept_covered(k, answer_stems, answer_compact)]
    missing = [k for k in key_concepts if k not in covered]

    recall = round(100 * len(covered) / len(key_concepts), 1) if key_concepts else 0.0
    has_reasoning = bool(REASONING_WORDS & set(_words(answer_text)))
    bonus = 20 if (has_reasoning and recall > 0) else 0
    understanding = round(min(100.0, recall * 0.8 + bonus), 1)

    if recall >= 70 and has_reasoning:
        answer_type = "correct_reasoned"
    elif recall >= 70:
        answer_type = "correct_shallow"
    else:
        answer_type = "partial"

    short = len(_words(answer_text)) < 8
    suggestions = ["Try to explain WHY, not only what. Use words like 'because'."] if not has_reasoning else []
    if missing:
        suggestions.append("Revise the missing ideas listed above and try again.")

    return AIEvaluation(
        recall_score=recall,
        understanding_score=understanding,
        answer_type=answer_type,
        correct_points=covered,
        missing_points=missing,
        incorrect_points=[],
        misconceptions=[],
        improvement_suggestions=suggestions,
        follow_up_question="Can you explain why this happens, in your own words?" if short else None,
        is_fallback=True,
    )


def evaluate_answer(question: Question, answer_text: str, concept_name: str = "") -> AIEvaluation:
    """Try Gemini; if the key is missing or the call/validation fails, use the flagged fallback."""
    if os.getenv("GEMINI_API_KEY"):
        try:
            return gemini_evaluate(question, concept_name, answer_text)
        except Exception as exc:  # network, quota, bad JSON, validation...
            log.warning("Gemini evaluation failed, using fallback: %s", exc)
    return fallback_evaluate(question, answer_text)