from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..mastery import get_level
from ..models import Attempt, Concept, Mastery, Question, RevisionSchedule, Student
from ..schemas import MasteryItem, ProgressResponse, RecentActivity, RevisionItem

router = APIRouter(prefix="/api/student", tags=["student"])


def _student(db: Session, student_id: int) -> Student:
    s = db.get(Student, student_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return s


def _mastery_items(db: Session, student_id: int) -> list[MasteryItem]:
    rows = {m.concept_id: m for m in db.scalars(select(Mastery).where(Mastery.student_id == student_id))}
    items = []
    for c in db.scalars(select(Concept).order_by(Concept.id)):
        m = rows.get(c.id)
        score = m.score if m else 0.0
        items.append(MasteryItem(concept_id=c.id, concept_name=c.name, mastery=score,
                                 attempts=m.attempt_count if m else 0, level=get_level(score)))
    return items


@router.get("/mastery", response_model=list[MasteryItem])
def mastery(student_id: int = 1, db: Session = Depends(get_db)):
    _student(db, student_id)
    return _mastery_items(db, student_id)


@router.get("/revisions", response_model=list[RevisionItem])
def revisions(student_id: int = 1, db: Session = Depends(get_db)):
    _student(db, student_id)
    rows = db.execute(
        select(RevisionSchedule, Concept.name)
        .join(Concept, RevisionSchedule.concept_id == Concept.id)
        .where(RevisionSchedule.student_id == student_id)
        .order_by(RevisionSchedule.due_date, Concept.id)
    ).all()
    return [RevisionItem(concept_id=r.concept_id, concept_name=name,
                         due_date=r.due_date.isoformat(), priority=r.priority) for r, name in rows]


@router.get("/progress", response_model=ProgressResponse)
def progress(student_id: int = 1, db: Session = Depends(get_db)):
    student = _student(db, student_id)
    items = [i for i in _mastery_items(db, student_id) if i.attempts > 0]

    total, avg_recall, avg_under = db.execute(
        select(func.count(Attempt.id), func.avg(Attempt.recall_score), func.avg(Attempt.understanding_score))
        .where(Attempt.student_id == student_id)).one()

    recent = db.execute(
        select(Attempt, Question.text, Concept.name)
        .join(Question, Attempt.question_id == Question.id)
        .join(Concept, Question.concept_id == Concept.id)
        .where(Attempt.student_id == student_id)
        .order_by(Attempt.created_at.desc(), Attempt.id.desc()).limit(5)).all()

    return ProgressResponse(
        name=student.name,
        overall_progress=round(sum(i.mastery for i in items) / len(items), 1) if items else 0.0,
        questions_attempted=total or 0,
        avg_recall=round(avg_recall or 0, 1),
        avg_understanding=round(avg_under or 0, 1),
        strong_concepts=[i.concept_name for i in items if i.level == "strong"],
        weak_concepts=[i.concept_name for i in items if i.level == "weak"],
        recent_activity=[RecentActivity(question=text, concept=cname, recall=a.recall_score,
                                        understanding=a.understanding_score,
                                        at=a.created_at.isoformat()) for a, text, cname in recent],
    )
