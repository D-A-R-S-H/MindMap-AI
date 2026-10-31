from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import RevisionSchedule

# level -> (days until revision, priority)
REVISION_RULES = {
    "Weak": (1, "high"),
    "Developing": (3, "medium"),
    "Strong": (7, "low"),
}


def schedule_revision(level: str, today: date | None = None) -> tuple[date, str]:
    """Pure function: work out the due date and priority for a mastery level."""
    days, priority = REVISION_RULES[level]
    start = today or date.today()
    return start + timedelta(days=days), priority


def upsert_revision(db: Session, student_id: int, concept_id: int, level: str) -> tuple[date, str]:
    """Create or update the student's revision row for a concept."""
    due_date, priority = schedule_revision(level)

    row = db.scalar(
        select(RevisionSchedule).where(
            RevisionSchedule.student_id == student_id,
            RevisionSchedule.concept_id == concept_id,
        )
    )
    if row is None:
        db.add(RevisionSchedule(
            student_id=student_id, concept_id=concept_id,
            due_date=due_date, priority=priority,
        ))
    else:
        row.due_date = due_date
        row.priority = priority

    return due_date, priority