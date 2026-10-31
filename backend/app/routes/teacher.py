from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Concept, Mastery, Misconception, Student
from ..schemas import ConceptAverage, MisconceptionCount, StudentRow, TeacherAnalyticsResponse

router = APIRouter(prefix="/api/teacher", tags=["teacher"])

NEEDS_TEACHING_BELOW = 55  # class average under this means the topic needs re-teaching


@router.get("/analytics", response_model=TeacherAnalyticsResponse)
def analytics(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Mastery, Concept.name, Student.name)
        .join(Concept, Mastery.concept_id == Concept.id)
        .join(Student, Mastery.student_id == Student.id)
        .where(Mastery.attempt_count > 0)).all()

    by_concept: dict[str, list[float]] = defaultdict(list)
    by_student: dict[str, list[tuple[float, str]]] = defaultdict(list)
    for m, cname, sname in rows:
        by_concept[cname].append(m.score)
        by_student[sname].append((m.score, cname))

    concepts = sorted((ConceptAverage(name=n, avg_mastery=round(sum(v) / len(v), 1))
                       for n, v in by_concept.items()), key=lambda c: c.avg_mastery)
    students = sorted((StudentRow(name=n, avg_mastery=round(sum(s for s, _ in v) / len(v), 1),
                                  weakest_concept=min(v)[1]) for n, v in by_student.items()),
                      key=lambda s: s.avg_mastery)
    all_scores = [m.score for m, _, _ in rows]

    misc = db.execute(
        select(Misconception.description, func.count(func.distinct(Misconception.student_id)))
        .group_by(Misconception.description)
        .order_by(func.count(func.distinct(Misconception.student_id)).desc()).limit(6)).all()

    return TeacherAnalyticsResponse(
        class_avg_mastery=round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0,
        concepts=concepts,
        common_misconceptions=[MisconceptionCount(text=t, count=c) for t, c in misc],
        students=students,
        needs_teaching=[c.name for c in concepts if c.avg_mastery < NEEDS_TEACHING_BELOW],
    )
