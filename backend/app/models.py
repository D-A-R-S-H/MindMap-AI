from datetime import date, datetime, timezone

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Concept(Base):
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    chapter: Mapped[str] = mapped_column(String(100), default="")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"))
    text: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(20))  # easy / medium / hard
    expected_answer: Mapped[str] = mapped_column(Text)
    key_concepts: Mapped[list] = mapped_column(JSON, default=list)
    is_diagnostic: Mapped[bool] = mapped_column(default=False)


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    answer_text: Mapped[str] = mapped_column(Text)
    recall_score: Mapped[float] = mapped_column(Float)
    understanding_score: Mapped[float] = mapped_column(Float)
    answer_type: Mapped[str] = mapped_column(String(30))
    feedback: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Mastery(Base):
    __tablename__ = "mastery"
    __table_args__ = (UniqueConstraint("student_id", "concept_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"))
    score: Mapped[float] = mapped_column(Float, default=0.0)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class Misconception(Base):
    __tablename__ = "misconceptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"))
    attempt_id: Mapped[int] = mapped_column(ForeignKey("attempts.id"))
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class RevisionSchedule(Base):
    __tablename__ = "revision_schedules"
    __table_args__ = (UniqueConstraint("student_id", "concept_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"))
    due_date: Mapped[date] = mapped_column(Date)
    priority: Mapped[str] = mapped_column(String(20))  # high / medium / low