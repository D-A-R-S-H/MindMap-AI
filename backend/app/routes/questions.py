from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Concept, Question
from ..schemas import QuestionOut

router = APIRouter(prefix="/api", tags=["questions"])


@router.get("/questions", response_model=list[QuestionOut])
def get_questions(
    type: Literal["diagnostic", "recall"] | None = None,
    concept_id: int | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Question, Concept.name).join(Concept, Question.concept_id == Concept.id)
    if type == "diagnostic":
        stmt = stmt.where(Question.is_diagnostic.is_(True))
    elif type == "recall":
        stmt = stmt.where(Question.is_diagnostic.is_(False))
    if concept_id is not None:
        stmt = stmt.where(Question.concept_id == concept_id)

    rows = db.execute(stmt.order_by(Question.id)).all()
    return [
        QuestionOut(
            id=q.id,
            concept_id=q.concept_id,
            concept_name=concept_name,
            question_text=q.text,
            difficulty=q.difficulty,
            expected_answer=q.expected_answer,
            key_concepts=q.key_concepts,
        )
        for q, concept_name in rows
    ]
