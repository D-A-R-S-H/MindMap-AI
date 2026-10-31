from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..ai_evaluator import evaluate_answer
from ..database import get_db
from ..mastery import combined_score, get_level, update_mastery
from ..models import Attempt, Concept, Mastery, Misconception, Question, Student
from ..revision import upsert_revision
from ..schemas import (
    EvaluateAnswerRequest,
    EvaluateAnswerResponse,
    MasteryUpdate,
    NextQuestion,
)

router = APIRouter(prefix="/api", tags=["evaluation"])

DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2}


def pick_next_question(db: Session, student_id: int, just_answered_id: int) -> NextQuestion | None:
    """Question engine: weakest concept first, easiest unanswered question first."""
    answered = set(
        db.scalars(select(Attempt.question_id).where(Attempt.student_id == student_id)).all()
    )
    answered.add(just_answered_id)

    weakest_first = db.scalars(
        select(Mastery.concept_id)
        .where(Mastery.student_id == student_id)
        .order_by(Mastery.score)
    ).all()
    rank = {concept_id: i for i, concept_id in enumerate(weakest_first)}

    rows = db.execute(
        select(Question, Concept.name)
        .join(Concept, Question.concept_id == Concept.id)
        .where(Question.id.not_in(list(answered)))
    ).all()
    if not rows:
        return None  # the student has answered every question

    question, concept_name = min(
        rows,
        key=lambda r: (rank.get(r[0].concept_id, 999), DIFFICULTY_ORDER.get(r[0].difficulty, 1), r[0].id),
    )
    return NextQuestion(
        question_id=question.id,
        concept=concept_name,
        difficulty=question.difficulty,
        question_text=question.text,
    )


@router.post("/evaluate-answer", response_model=EvaluateAnswerResponse)
def evaluate(payload: EvaluateAnswerRequest, db: Session = Depends(get_db)):
    student = db.get(Student, payload.student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    question = db.get(Question, payload.question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    concept = db.get(Concept, question.concept_id)

    # 1. Score the answer (Gemini, or the fallback if Gemini fails)
    result = evaluate_answer(question, payload.answer_text)

    # 2. Save the attempt (flush so attempt.id exists for the misconception rows)
    attempt = Attempt(
        student_id=student.id,
        question_id=question.id,
        answer_text=payload.answer_text,
        recall_score=result.recall_score,
        understanding_score=result.understanding_score,
        answer_type=result.answer_type,
        feedback=result.feedback,
    )
    db.add(attempt)
    db.flush()

    # 3. Update mastery (deterministic Python maths, not AI)
    mastery = db.scalar(
        select(Mastery).where(Mastery.student_id == student.id, Mastery.concept_id == concept.id)
    )
    if mastery is None:
        # First time on this concept: start from this answer's score
        old_score = 0.0
        new_score = round(combined_score(result.recall_score, result.understanding_score), 1)
        mastery = Mastery(student_id=student.id, concept_id=concept.id, score=new_score, attempt_count=1)
        db.add(mastery)
    else:
        old_score = mastery.score
        new_score = update_mastery(
            old_score, result.recall_score, result.understanding_score, mastery.attempt_count
        )
        mastery.score = new_score
        mastery.attempt_count += 1
    level = get_level(new_score)

    # 4. Store misconceptions found by the AI
    for description in result.misconceptions:
        db.add(Misconception(
            student_id=student.id,
            concept_id=concept.id,
            attempt_id=attempt.id,
            description=description,
        ))

    # 5. Reschedule revision from the new level
    due_date, _priority = upsert_revision(db, student.id, concept.id, level)

    # 6. Choose the next question (flush first so it sees the new mastery)
    db.flush()
    next_question = pick_next_question(db, student.id, question.id)

    db.commit()

    return EvaluateAnswerResponse(
        recall_score=result.recall_score,
        understanding_score=result.understanding_score,
        answer_type=result.answer_type,
        feedback=result.feedback,
        misconceptions=result.misconceptions,
        mastery_update=MasteryUpdate(
            concept=concept.name, old_score=old_score, new_score=new_score, level=level
        ),
        next_question=next_question,
        revision_date=due_date,
    )