from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..mastery import get_level
from ..models import Attempt, Concept, Mastery, Question, RevisionSchedule, Student
from ..schemas import (
    MasteryItem,
    ProgressResponse,
    RecentActivity,
    RevisionItem,
    StudentMasteryResponse,
    StudentRevisionsResponse,
)

router = APIRouter(prefix="/api/student", tags=["student"])


def _get_student(db: Session, student_id: int) -> Student:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.get("/progress", response_model=ProgressResponse)
def progress(student_id: int = 1, db: Session = Depends(get_db)):
    _get_student(db, student_id)

    overall = db.scalar(
        select(func.avg(Mastery.score)).where(Mastery.student_id == student_id)
    ) or 0

    total, avg_recall, avg_understanding = db.execute(
        select(
            func.count(Attempt.id),
            func.avg(Attempt.recall_score),
            func.avg(Attempt.understanding_score),
        ).where(Attempt.student_id == student_id)
    ).one()

    recent = db.execute(
        select(Attempt, Concept.name)
        .join(Question, Attempt.question_id == Question.id)
        .join(Concept, Question.concept_id == Concept.id)
        .where(Attempt.student_id == student_id)
        .order_by(Attempt.created_at.desc(), Attempt.id.desc())
        .limit(5)
    ).all()

    return ProgressResponse(
        overall_progress=round(overall, 1),
        total_attempts=total,
        average_recall=round(avg_recall or 0, 1),
        average_understanding=round(avg_understanding or 0, 1),
        recent_activity=[
            RecentActivity(
                concept=name,
                answer_type=attempt.answer_type,
                recall_score=attempt.recall_score,
                understanding_score=attempt.understanding_score,
                created_at=attempt.created_at,
            )
            for attempt, name in recent
        ],
    )


@router.get("/mastery", response_model=StudentMasteryResponse)
def student_mastery(student_id: int = 1, db: Session = Depends(get_db)):
    _get_student(db, student_id)

    rows = db.execute(
        select(Concept.name, Mastery.score)
        .join(Mastery, Mastery.concept_id == Concept.id)
        .where(Mastery.student_id == student_id)
        .order_by(Mastery.score)
    ).all()

    return StudentMasteryResponse(
        mastery=[MasteryItem(concept=name, score=score, level=get_level(score)) for name, score in rows]
    )


@router.get("/revisions", response_model=StudentRevisionsResponse)
def student_revisions(student_id: int = 1, db: Session = Depends(get_db)):
    _get_student(db, student_id)

    rows = db.execute(
        select(Concept.name, RevisionSchedule.due_date, RevisionSchedule.priority)
        .join(RevisionSchedule, RevisionSchedule.concept_id == Concept.id)
        .where(RevisionSchedule.student_id == student_id)
        .order_by(RevisionSchedule.due_date, Concept.name)
    ).all()

    return StudentRevisionsResponse(
        revisions=[RevisionItem(concept=name, due_date=due, priority=priority) for name, due, priority in rows]
    )