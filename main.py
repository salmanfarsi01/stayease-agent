import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from api.database import init_db
from api.routes import router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="StayEase AI Agent API",
    description="AI-powered accommodation booking assistant for Bangladesh",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

@app.on_event("startup")
def on_startup() -> None:
    init_db()

app.include_router(router)

@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "StayEase AI Agent"}

@app.get("/chat")
def serve_chat():
    return FileResponse(os.path.join(BASE_DIR, "chatbot.html"))