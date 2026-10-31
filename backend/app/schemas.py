from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

# ---- Shared value types ----
AnswerType = Literal[
    "correct_reasoned",
    "correct_shallow",
    "partial",
    "misconception",
    "paraphrased_correct",
]
MasteryLevel = Literal["Weak", "Developing", "Strong"]
Priority = Literal["high", "medium", "low"]
Score = Field(ge=0, le=100)


# ---- GET /api/health ----
class HealthResponse(BaseModel):
    status: str
    ai_mode: Literal["gemini", "fallback"]


# ---- GET /api/questions ----
class QuestionOut(BaseModel):
    question_id: int
    concept: str
    difficulty: str
    question_text: str
    expected_answer: str
    key_concepts: list[str]


# ---- POST /api/diagnostic/submit ----
class DiagnosticAnswer(BaseModel):
    question_id: int
    answer_text: str = Field(min_length=1, max_length=2000)


class DiagnosticSubmitRequest(BaseModel):
    student_id: int = 1
    answers: list[DiagnosticAnswer] = Field(min_length=1)


class StudentProfile(BaseModel):
    student_id: int
    name: str


class DiagnosticSubmitResponse(BaseModel):
    student: StudentProfile
    strong_concepts: list[str]
    weak_concepts: list[str]


# ---- Gemini's output (validated in Stage 11) ----
class AIEvaluation(BaseModel):
    recall_score: float = Score
    understanding_score: float = Score
    answer_type: AnswerType
    feedback: str
    misconceptions: list[str] = []


# ---- POST /api/evaluate-answer ----
class EvaluateAnswerRequest(BaseModel):
    student_id: int = 1
    question_id: int
    answer_text: str = Field(min_length=1, max_length=2000)


class MasteryUpdate(BaseModel):
    concept: str
    old_score: float
    new_score: float
    level: MasteryLevel


class NextQuestion(BaseModel):
    question_id: int
    concept: str
    difficulty: str
    question_text: str


class EvaluateAnswerResponse(BaseModel):
    recall_score: float
    understanding_score: float
    answer_type: AnswerType
    feedback: str
    misconceptions: list[str]
    mastery_update: MasteryUpdate
    next_question: Optional[NextQuestion] = None
    revision_date: date


# ---- GET /api/student/progress ----
class RecentActivity(BaseModel):
    concept: str
    answer_type: AnswerType
    recall_score: float
    understanding_score: float
    created_at: datetime


class ProgressResponse(BaseModel):
    overall_progress: float  # average mastery across concepts, 0-100
    total_attempts: int
    average_recall: float
    average_understanding: float
    recent_activity: list[RecentActivity]


# ---- GET /api/student/mastery ----
class MasteryItem(BaseModel):
    concept: str
    score: float
    level: MasteryLevel


class StudentMasteryResponse(BaseModel):
    mastery: list[MasteryItem]


# ---- GET /api/student/revisions ----
class RevisionItem(BaseModel):
    concept: str
    due_date: date
    priority: Priority


class StudentRevisionsResponse(BaseModel):
    revisions: list[RevisionItem]


# ---- GET /api/teacher/analytics ----
class ConceptAverage(BaseModel):
    concept: str
    average_mastery: float


class MisconceptionCount(BaseModel):
    description: str
    count: int


class StudentAttention(BaseModel):
    student_id: int
    name: str
    average_mastery: float
    weak_concepts: list[str]


class TeacherAnalyticsResponse(BaseModel):
    class_average_mastery: float
    concept_averages: list[ConceptAverage]
    common_misconceptions: list[MisconceptionCount]
    students_needing_attention: list[StudentAttention]