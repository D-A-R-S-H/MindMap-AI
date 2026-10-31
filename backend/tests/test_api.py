"""API tests against the agreed contract. Uses a throw-away in-memory database."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.seed import seed_database

GOOD = ("Because a mirror is smooth the rays stay parallel after regular reflection and form an image, "
        "but a wall is rough so rays scatter in many directions and no image forms")


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)  # tests always use the fallback evaluator
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with Session() as db:
        seed_database(db)

    def override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok", "ai_mode": "fallback"}


def test_questions_shape_and_filters(client):
    allq = client.get("/api/questions").json()
    diag = client.get("/api/questions?type=diagnostic").json()
    rec = client.get("/api/questions?type=recall").json()
    assert len(allq) == 18 and len(diag) == 10 and len(rec) == 8
    assert {"id", "concept_id", "concept_name", "question_text", "difficulty",
            "expected_answer", "key_concepts"} <= set(allq[0])
    assert isinstance(allq[0]["difficulty"], int)
    assert len({q["concept_name"] for q in allq}) == 9


def test_diagnostic_submit_builds_profile(client):
    qs = client.get("/api/questions?type=diagnostic").json()
    r = client.post("/api/diagnostic/submit", json={"student_id": 1, "answers": [
        {"question_id": qs[0]["id"], "answer_text": qs[0]["expected_answer"]},
        {"question_id": qs[1]["id"], "answer_text": "no idea"},
    ]})
    assert r.status_code == 200
    body = r.json()
    assert {p["level"] for p in body["profile"]} <= {"weak", "developing", "strong"}
    assert qs[0]["concept_name"] in body["strong_concepts"]
    assert qs[1]["concept_name"] in body["weak_concepts"]


def test_diagnostic_rejects_blank_answer(client):
    r = client.post("/api/diagnostic/submit", json={"answers": [{"question_id": 1, "answer_text": ""}]})
    assert r.status_code == 422


def test_evaluate_answer_full_journey(client):
    q = client.get("/api/questions?type=recall").json()[0]
    r = client.post("/api/evaluate-answer", json={"question_id": q["id"], "answer_text": GOOD})
    assert r.status_code == 200
    d = r.json()
    assert d["is_fallback"] is True                       # never pretend fallback is real AI
    assert 0 <= d["recall_score"] <= 100 and 0 <= d["understanding_score"] <= 100
    assert d["updated_mastery"]["new"] > d["updated_mastery"]["old"]
    assert d["next_question"]["id"] != q["id"]
    assert len(d["next_revision_date"]) == 10

    assert client.get("/api/student/progress").json()["questions_attempted"] == 1
    assert any(m["attempts"] == 1 for m in client.get("/api/student/mastery").json())
    assert len(client.get("/api/student/revisions").json()) == 1


def test_short_answer_gets_follow_up_question(client):
    q = client.get("/api/questions").json()[0]
    d = client.post("/api/evaluate-answer", json={"question_id": q["id"], "answer_text": "light bends"}).json()
    assert d["follow_up_question"]


def test_unknown_ids_return_404(client):
    assert client.post("/api/evaluate-answer", json={"question_id": 9999, "answer_text": "x"}).status_code == 404
    assert client.get("/api/student/progress?student_id=99").status_code == 404


def test_fresh_student_endpoints_are_empty_but_valid(client):
    p = client.get("/api/student/progress").json()
    assert p["questions_attempted"] == 0 and p["overall_progress"] == 0
    assert p["recent_activity"] == [] and p["name"]
    assert len(client.get("/api/student/mastery").json()) == 9
    assert client.get("/api/student/revisions").json() == []


def test_teacher_analytics_uses_sample_class(client):
    t = client.get("/api/teacher/analytics").json()
    assert len(t["students"]) == 8 and len(t["concepts"]) == 9
    assert t["needs_teaching"] and t["common_misconceptions"]
    assert {"Mirror formula", "Lens formula"} <= set(t["needs_teaching"])