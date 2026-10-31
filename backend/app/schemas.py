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
MasteryLevel = Literal["weak", "developing", "strong"]
Priority = Literal["high", "medium", "low"]
Score = Field(ge=0, le=100)


# ---- GET /api/health ----
class HealthResponse(BaseModel):
    status: str
    ai_mode: Literal["gemini", "fallback"]


# ---- GET /api/questions ----
class QuestionOut(BaseModel):
    id: int
    concept_id: int
    concept_name: str
    question_text: str
    difficulty: int
    expected_answer: str
    key_concepts: list[str]


# ---- POST /api/diagnostic/submit ----
class DiagnosticAnswer(BaseModel):
    question_id: int
    answer_text: str = Field(min_length=1, max_length=4000)


class DiagnosticSubmitRequest(BaseModel):
    student_id: int = 1
    answers: list[DiagnosticAnswer] = Field(min_length=1)


class ProfileItem(BaseModel):
    concept_id: int
    concept_name: str
    mastery: float
    level: MasteryLevel


class DiagnosticSubmitResponse(BaseModel):
    profile: list[ProfileItem]
    weak_concepts: list[str]
    strong_concepts: list[str]


# ---- Gemini's output (validated with Pydantic) ----
class AIEvaluation(BaseModel):
    recall_score: float = Score
    understanding_score: float = Score
    answer_type: AnswerType
    correct_points: list[str] = []
    missing_points: list[str] = []
    incorrect_points: list[str] = []
    misconceptions: list[str] = []
    improvement_suggestions: list[str] = []
    follow_up_question: Optional[str] = None
    is_fallback: bool = False


# ---- POST /api/evaluate-answer ----
class EvaluateAnswerRequest(BaseModel):
    student_id: int = 1
    question_id: int
    answer_text: str = Field(min_length=1, max_length=4000)


class UpdatedMastery(BaseModel):
    concept_id: int
    concept_name: str
    old: float
    new: float


class NextQuestion(BaseModel):
    id: int
    question_text: str
    concept_name: str


class EvaluateAnswerResponse(AIEvaluation):
    updated_mastery: UpdatedMastery
    next_question: Optional[NextQuestion] = None
    next_revision_date: str  # YYYY-MM-DD


# ---- GET /api/student/progress ----
class RecentActivity(BaseModel):
    question: str
    concept: str
    recall: float
    understanding: float
    at: str


class ProgressResponse(BaseModel):
    name: str
    overall_progress: float
    questions_attempted: int
    avg_recall: float
    avg_understanding: float
    strong_concepts: list[str]
    weak_concepts: list[str]
    recent_activity: list[RecentActivity]


# ---- GET /api/student/mastery ----
class MasteryItem(BaseModel):
    concept_id: int
    concept_name: str
    mastery: float
    attempts: int
    level: MasteryLevel


# ---- GET /api/student/revisions ----
class RevisionItem(BaseModel):
    concept_id: int
    concept_name: str
    due_date: str
    priority: Priority


# ---- GET /api/teacher/analytics ----
class ConceptAverage(BaseModel):
    name: str
    avg_mastery: float


class MisconceptionCount(BaseModel):
    text: str
    count: int


class StudentRow(BaseModel):
    name: str
    avg_mastery: float
    weakest_concept: str


class TeacherAnalyticsResponse(BaseModel):
    class_avg_mastery: float
    concepts: list[ConceptAverage]
    common_misconceptions: list[MisconceptionCount]
    students: list[StudentRow]
    needs_teaching: list[str]
