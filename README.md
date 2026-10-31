# Mindmap AI

An AI-powered learning platform that evaluates students' understanding rather than
matching answers to a textbook.

## Run the backend

```
cd backend
python -m venv ..\.venv
..\.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env      # then put your Gemini key in .env
python -m uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000 (interactive docs at /docs)
- Run tests: `python -m pytest -v` (from the backend folder)

## Endpoints

| Method | Endpoint | Notes |
| --- | --- | --- |
| GET | /api/health | status, ai_mode |
| GET | /api/questions | optional `?diagnostic=true`, `?concept=...` |
| POST | /api/diagnostic/submit | body: student_id, answers[{question_id, answer_text}] |
| POST | /api/evaluate-answer | body: student_id, question_id, answer_text |
| GET | /api/student/progress | optional `?student_id=1` |
| GET | /api/student/mastery | optional `?student_id=1` |
| GET | /api/student/revisions | optional `?student_id=1` |
| GET | /api/teacher/analytics | |

No login in the MVP. The demo student has id 1.