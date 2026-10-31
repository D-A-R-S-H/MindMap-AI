# MindMap AI

Adaptive, voice-first AI study tutor. Students dictate answers (Wispr Flow works in any text box;
there is no direct Wispr API integration) and Gemini evaluates understanding, not wording.
Demo content: Class 10 Physics, Light: Reflection and Refraction.

## Run the backend (port 8000)
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env         # Mac/Linux: cp .env.example .env, then add GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```
The database is created and seeded automatically on start. If you change `app/seed.py`,
delete `backend/mindmap.db` and restart. API docs: http://localhost:8000/docs
Without a key the app still works and clearly labels results as "Demo fallback evaluation".

Tests: `cd backend && python -m pytest`

## Run the frontend (port 5173)
```bash
cd frontend
npm install
npm run dev
```
`src/api/client.js` has `USE_MOCK`. `false` = real backend, `true` = fake data.

## Journey
Diagnostic -> Speak & Recall -> AI evaluation -> mastery update -> next question + revision date.
