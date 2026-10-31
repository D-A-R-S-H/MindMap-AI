from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..ai_evaluator import evaluate_answer
from ..database import get_db
from ..mastery import get_level
from ..models import Attempt, Concept, Mastery, Question, Student
from ..schemas import DiagnosticSubmitRequest, DiagnosticSubmitResponse, StudentProfile
from ..revision import upsert_revision

router = APIRouter(prefix="/api", tags=["diagnostic"])


@router.post("/diagnostic/submit", response_model=DiagnosticSubmitResponse)
def submit_diagnostic(payload: DiagnosticSubmitRequest, db: Session = Depends(get_db)):
    student = db.get(Student, payload.student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    # concept_id -> list of combined scores from this submission
    concept_scores: dict[int, list[float]] = {}

    for item in payload.answers:
        question = db.get(Question, item.question_id)
        if question is None:
            raise HTTPException(status_code=404, detail=f"Question {item.question_id} not found")

        result = evaluate_answer(question, item.answer_text)

        db.add(Attempt(
            student_id=student.id,
            question_id=question.id,
            answer_text=item.answer_text,
            recall_score=result.recall_score,
            understanding_score=result.understanding_score,
            answer_type=result.answer_type,
            feedback=result.feedback,
        ))

        combined = (result.recall_score + result.understanding_score) / 2
        concept_scores.setdefault(question.concept_id, []).append(combined)

    strong, weak = [], []

    for concept_id, scores in concept_scores.items():
        score = round(sum(scores) / len(scores), 1)

        mastery = db.scalar(
            select(Mastery).where(
                Mastery.student_id == student.id,
                Mastery.concept_id == concept_id,
            )
        )
        if mastery is None:
            mastery = Mastery(student_id=student.id, concept_id=concept_id, attempt_count=0)
            db.add(mastery)
        mastery.score = score
        mastery.attempt_count += len(scores)

        concept_name = db.get(Concept, concept_id).name
        level = get_level(score)
        upsert_revision(db, student.id, concept_id, level)
        if level == "Strong":
            strong.append(concept_name)
        elif level == "Weak":
            weak.append(concept_name)

    db.commit()

    return DiagnosticSubmitResponse(
        student=StudentProfile(student_id=student.id, name=student.name),
        strong_concepts=strong,
        weak_concepts=weak,
    )