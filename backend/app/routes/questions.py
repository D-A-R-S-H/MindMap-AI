from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Concept, Question
from ..schemas import QuestionOut

router = APIRouter(prefix="/api", tags=["questions"])


@router.get("/questions", response_model=list[QuestionOut])
def get_questions(
    diagnostic: bool | None = None,
    concept: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Question, Concept.name).join(Concept, Question.concept_id == Concept.id)

    if diagnostic is not None:
        stmt = stmt.where(Question.is_diagnostic == diagnostic)
    if concept:
        stmt = stmt.where(Concept.name == concept)

    rows = db.execute(stmt.order_by(Question.id)).all()

    return [
        QuestionOut(
            question_id=q.id,
            concept=concept_name,
            difficulty=q.difficulty,
            question_text=q.text,
            expected_answer=q.expected_answer,
            key_concepts=q.key_concepts,
        )
        for q, concept_name in rows
    ]