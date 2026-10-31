import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401  (registers the tables with Base)
from .database import Base, SessionLocal, engine
from .routes import questions
from .schemas import HealthResponse
from .seed import seed_database

load_dotenv()

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_database(db)

app = FastAPI(title="Mindmap AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router)


@app.get("/api/health", response_model=HealthResponse)
def health():
    ai_mode = "gemini" if os.getenv("GEMINI_API_KEY") else "fallback"
    return {"status": "ok", "ai_mode": ai_mode}