import os
from .database import Base, engine
from . import models 
from dotenv import load_dotenv
Base.metadata.create_all(bind=engine)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import HealthResponse

load_dotenv()  # reads backend/.env into environment variables

app = FastAPI(title="Mindmap AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health():
    ai_mode = "gemini" if os.getenv("GEMINI_API_KEY") else "fallback"
    return {"status": "ok", "ai_mode": ai_mode}