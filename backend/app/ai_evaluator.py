import re

from .models import Question
from .schemas import AIEvaluation

STOPWORDS = {
    "the", "and", "are", "for", "with", "from", "that", "this", "was",
    "has", "not", "its", "into", "than", "then", "also",
}
REASONING_WORDS = {"because", "so", "therefore", "since", "hence", "thus"}


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z]+", text.lower())


def _content_stems(text: str) -> set[str]:
    # First 5 letters of each meaningful word, so "proportional" matches "proportion"
    return {w[:5] for w in _words(text) if len(w) >= 3 and w not in STOPWORDS}


def _concept_covered(key_concept: str, answer_stems: set[str], answer_compact: str) -> bool:
    needed = _content_stems(key_concept)
    if not needed:
        # Formula-like ideas such as "V = IR": compare with spaces removed
        return re.sub(r"\s+", "", key_concept.lower()) in answer_compact
    return len(needed & answer_stems) / len(needed) >= 0.5


def fallback_evaluate(question: Question, answer_text: str) -> AIEvaluation:
    """A simple keyword check. It cannot truly judge understanding."""
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

    feedback = f"Basic keyword check (AI evaluator not connected yet): you covered {len(covered)} of {len(key_concepts)} key ideas."
    if missing:
        feedback += " Missing: " + "; ".join(missing) + "."

    return AIEvaluation(
        recall_score=recall,
        understanding_score=understanding,
        answer_type=answer_type,
        feedback=feedback,
        misconceptions=[],
    )


def evaluate_answer(question: Question, answer_text: str) -> AIEvaluation:
    # Stage 11: try Gemini first, and fall back to the keyword check if it fails.
    return fallback_evaluate(question, answer_text)