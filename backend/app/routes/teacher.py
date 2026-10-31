from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..mastery import get_level
from ..models import Concept, Mastery, Misconception, Student
from ..schemas import (
    ConceptAverage,
    MisconceptionCount,
    StudentAttention,
    TeacherAnalyticsResponse,
)

router = APIRouter(prefix="/api/teacher", tags=["teacher"])

ATTENTION_THRESHOLD = 60  # students with average mastery below this need attention


@router.get("/analytics", response_model=TeacherAnalyticsResponse)
def analytics(db: Session = Depends(get_db)):
    class_average = db.scalar(select(func.avg(Mastery.score))) or 0

    concept_rows = db.execute(
        select(Concept.name, func.avg(Mastery.score))
        .join(Mastery, Mastery.concept_id == Concept.id)
        .group_by(Concept.name)
        .order_by(Concept.name)
    ).all()

    misconception_rows = db.execute(
        select(Misconception.description, func.count(Misconception.id))
        .group_by(Misconception.description)
        .order_by(func.count(Misconception.id).desc())
        .limit(5)
    ).all()

    # One row per (student, concept) so we can group in Python
    student_rows = db.execute(
        select(Student.id, Student.name, Concept.name, Mastery.score)
        .select_from(Student)
        .join(Mastery, Mastery.student_id == Student.id)
        .join(Concept, Mastery.concept_id == Concept.id)
    ).all()

    by_student: dict[int, dict] = {}
    for student_id, student_name, concept_name, score in student_rows:
        entry = by_student.setdefault(
            student_id, {"name": student_name, "scores": [], "weak": []}
        )
        entry["scores"].append(score)
        if get_level(score) == "Weak":
            entry["weak"].append(concept_name)

    attention = []
    for student_id, entry in by_student.items():
        average = sum(entry["scores"]) / len(entry["scores"])
        if average < ATTENTION_THRESHOLD:
            attention.append(StudentAttention(
                student_id=student_id,
                name=entry["name"],
                average_mastery=round(average, 1),
                weak_concepts=entry["weak"],
            ))
    attention.sort(key=lambda s: s.average_mastery)

    return TeacherAnalyticsResponse(
        class_average_mastery=round(class_average, 1),
        concept_averages=[ConceptAverage(concept=n, average_mastery=round(a, 1)) for n, a in concept_rows],
        common_misconceptions=[MisconceptionCount(description=d, count=c) for d, c in misconception_rows],
        students_needing_attention=attention,
    )