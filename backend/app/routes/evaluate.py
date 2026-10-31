from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..ai_evaluator import evaluate_answer
from ..database import get_db
from ..mastery import DEFAULT_PRIOR, combined_score, get_level, update_mastery
from ..models import Attempt, Concept, Mastery, Misconception, Question, Student
from ..revision import upsert_revision
from ..schemas import EvaluateAnswerRequest, EvaluateAnswerResponse, NextQuestion, UpdatedMastery

router = APIRouter(prefix="/api", tags=["evaluate"])


def pick_next_question(db: Session, student_id: int, answered: Question, last_score: float):
    """Weakest concept first; difficulty one step up after a strong answer, one down after a weak one."""
    concepts = db.scalars(select(Concept).order_by(Concept.id)).all()
    mastery = {m.concept_id: m.score for m in
               db.scalars(select(Mastery).where(Mastery.student_id == student_id))}
    target_concept = min(concepts, key=lambda c: (mastery.get(c.id, DEFAULT_PRIOR), c.id))

    step = 1 if last_score >= 75 else -1 if last_score < 50 else 0
    target_diff = max(1, min(3, answered.difficulty + step))

    attempts = dict(db.execute(
        select(Attempt.question_id, func.count()).where(Attempt.student_id == student_id)
        .group_by(Attempt.question_id)).all())

    def best(candidates):
        return min(candidates, key=lambda q: (attempts.get(q.id, 0), abs(q.difficulty - target_diff), q.id),
                   default=None)

    same_concept = db.scalars(select(Question).where(
        Question.concept_id == target_concept.id, Question.id != answered.id)).all()
    q = best(same_concept) or best(db.scalars(select(Question).where(Question.id != answered.id)).all())
    return q


@router.post("/evaluate-answer", response_model=EvaluateAnswerResponse)
def evaluate(payload: EvaluateAnswerRequest, db: Session = Depends(get_db)):
    student = db.get(Student, payload.student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    question = db.get(Question, payload.question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    concept = db.get(Concept, question.concept_id)

    result = evaluate_answer(question, payload.answer_text, concept.name)  # never raises: falls back

    row = db.scalar(select(Mastery).where(
        Mastery.student_id == student.id, Mastery.concept_id == concept.id))
    if row is None:
        row = Mastery(student_id=student.id, concept_id=concept.id, score=DEFAULT_PRIOR, attempt_count=0)
        db.add(row)
    old = row.score
    new = update_mastery(old, result.recall_score, result.understanding_score, row.attempt_count)
    row.score = new
    row.attempt_count += 1

    attempt = Attempt(
        student_id=student.id, question_id=question.id, answer_text=payload.answer_text,
        recall_score=result.recall_score, understanding_score=result.understanding_score,
        answer_type=result.answer_type, feedback="; ".join(result.missing_points),
    )
    db.add(attempt)
    db.flush()
    for text in result.misconceptions:
        db.add(Misconception(student_id=student.id, concept_id=concept.id,
                             attempt_id=attempt.id, description=text))

    due_date, _ = upsert_revision(db, student.id, concept.id, get_level(new))
    nxt = pick_next_question(db, student.id, question,
                            combined_score(result.recall_score, result.understanding_score))
    next_q = None
    if nxt is not None:
        next_q = NextQuestion(id=nxt.id, question_text=nxt.text,
                              concept_name=db.get(Concept, nxt.concept_id).name)
    db.commit()

    return EvaluateAnswerResponse(
        **result.model_dump(),
        updated_mastery=UpdatedMastery(concept_id=concept.id, concept_name=concept.name, old=old, new=new),
        next_question=next_q,
        next_revision_date=due_date.isoformat(),
    )
