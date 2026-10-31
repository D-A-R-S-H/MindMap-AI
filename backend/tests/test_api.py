GOOD_ANSWER = (
    "At constant temperature the current through a conductor is directly proportional "
    "to the potential difference across it, V = IR, so if voltage doubles the current "
    "doubles and resistance stays constant."
)
ANSWER_TYPES = {
    "correct_reasoned", "correct_shallow", "partial", "misconception", "paraphrased_correct",
}


def test_health(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["ai_mode"] in {"gemini", "fallback"}


def test_questions(client):
    assert len(client.get("/api/questions").json()) == 12
    assert len(client.get("/api/questions?diagnostic=true").json()) == 6


def test_diagnostic_submit(client):
    response = client.post("/api/diagnostic/submit", json={
        "student_id": 1,
        "answers": [
            {"question_id": 1, "answer_text": GOOD_ANSWER},
            {"question_id": 5, "answer_text": "I don't know"},
        ],
    })
    assert response.status_code == 200
    body = response.json()
    assert "Ohm's Law" in body["strong_concepts"]
    assert "Electric Power and Heating Effect" in body["weak_concepts"]


def test_diagnostic_unknown_student(client):
    response = client.post("/api/diagnostic/submit", json={
        "student_id": 99,
        "answers": [{"question_id": 1, "answer_text": "anything"}],
    })
    assert response.status_code == 404


def test_evaluate_answer_flow(client):
    response = client.post("/api/evaluate-answer", json={
        "student_id": 1, "question_id": 1, "answer_text": GOOD_ANSWER,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["answer_type"] in ANSWER_TYPES
    assert body["mastery_update"]["concept"] == "Ohm's Law"
    assert body["mastery_update"]["level"] == "Strong"
    assert body["next_question"]["question_id"] != 1
    assert body["revision_date"]

    # The other endpoints should now reflect this attempt
    assert client.get("/api/student/progress").json()["total_attempts"] == 1
    mastery = client.get("/api/student/mastery").json()["mastery"]
    assert mastery[0]["concept"] == "Ohm's Law"
    assert client.get("/api/student/revisions").json()["revisions"][0]["priority"] == "low"


def test_evaluate_rejects_empty_answer(client):
    response = client.post("/api/evaluate-answer", json={
        "student_id": 1, "question_id": 1, "answer_text": "",
    })
    assert response.status_code == 422


def test_new_student_endpoints_are_empty(client):
    progress = client.get("/api/student/progress").json()
    assert progress["total_attempts"] == 0
    assert progress["overall_progress"] == 0
    assert client.get("/api/student/mastery").json()["mastery"] == []
    assert client.get("/api/student/revisions").json()["revisions"] == []
    assert client.get("/api/student/progress?student_id=99").status_code == 404


def test_teacher_analytics_after_good_answer(client):
    client.post("/api/evaluate-answer", json={
        "student_id": 1, "question_id": 1, "answer_text": GOOD_ANSWER,
    })
    body = client.get("/api/teacher/analytics").json()
    assert body["class_average_mastery"] == 100.0
    assert body["students_needing_attention"] == []


def test_teacher_flags_struggling_student(client):
    client.post("/api/diagnostic/submit", json={
        "student_id": 1,
        "answers": [{"question_id": 1, "answer_text": "I don't know"}],
    })
    flagged = client.get("/api/teacher/analytics").json()["students_needing_attention"]
    assert flagged[0]["student_id"] == 1
    assert "Ohm's Law" in flagged[0]["weak_concepts"]