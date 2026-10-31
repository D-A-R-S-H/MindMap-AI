from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..ai_evaluator import evaluate_answer
from ..database import get_db
from ..mastery import get_level
from ..models import Attempt, Concept, Mastery, Misconception, Question, Student
from ..revision import upsert_revision
from ..schemas import DiagnosticSubmitRequest, DiagnosticSubmitResponse, ProfileItem

router = APIRouter(prefix="/api", tags=["diagnostic"])


@router.post("/diagnostic/submit", response_model=DiagnosticSubmitResponse)
def submit_diagnostic(payload: DiagnosticSubmitRequest, db: Session = Depends(get_db)):
    student = db.get(Student, payload.student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    concept_scores: dict[int, list[float]] = {}

    for item in payload.answers:
        question = db.get(Question, item.question_id)
        if question is None:
            raise HTTPException(status_code=404, detail=f"Question {item.question_id} not found")
        concept = db.get(Concept, question.concept_id)

        result = evaluate_answer(question, item.answer_text, concept.name)

        attempt = Attempt(
            student_id=student.id,
            question_id=question.id,
            answer_text=item.answer_text,
            recall_score=result.recall_score,
            understanding_score=result.understanding_score,
            answer_type=result.answer_type,
            feedback="; ".join(result.missing_points),
        )
        db.add(attempt)
        db.flush()
        for text in result.misconceptions:
            db.add(Misconception(student_id=student.id, concept_id=concept.id,
                                 attempt_id=attempt.id, description=text))

        concept_scores.setdefault(question.concept_id, []).append(
            (result.recall_score + result.understanding_score) / 2
        )

    for concept_id, scores in concept_scores.items():
        row = db.scalar(select(Mastery).where(
            Mastery.student_id == student.id, Mastery.concept_id == concept_id))
        if row is None:
            row = Mastery(student_id=student.id, concept_id=concept_id, attempt_count=0)
            db.add(row)
        row.score = round(sum(scores) / len(scores), 1)  # the diagnostic sets the starting level
        row.attempt_count = (row.attempt_count or 0) + len(scores)
        upsert_revision(db, student.id, concept_id, get_level(row.score))

    db.commit()

    rows = db.execute(
        select(Mastery, Concept.name)
        .join(Concept, Mastery.concept_id == Concept.id)
        .where(Mastery.student_id == student.id, Mastery.attempt_count > 0)
        .order_by(Concept.id)
    ).all()
    profile = [ProfileItem(concept_id=m.concept_id, concept_name=name, mastery=m.score,
                           level=get_level(m.score)) for m, name in rows]
    return DiagnosticSubmitResponse(
        profile=profile,
        weak_concepts=[p.concept_name for p in profile if p.level == "weak"],
        strong_concepts=[p.concept_name for p in profile if p.level == "strong"],
    )
