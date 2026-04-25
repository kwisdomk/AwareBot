from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from app.state import handle, get
from app.agent import run_agent
from typing import Union

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("GOOGLE_API_KEY missing in environment")

app = FastAPI(title="Soko Akili", description="Intent-aware market decision agent for Kenyan farmers.")

# Mount static directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def serve_ui():
    return FileResponse("app/static/index.html")

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    stage: str
    type: str
    message: Union[dict, str]

@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    session_id = payload.session_id
    message = payload.message

    result = handle(session_id, message)
    current_state = get(session_id)

    # Onboarding complete → run agent
    if isinstance(result, dict):
        try:
            decision = run_agent(result)
            return ChatResponse(
                session_id=session_id,
                stage=str(current_state["stage"]),
                type="ai_response",
                message=decision
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    if not result:
        result = "⚠️ Something went wrong. Try again."

    return ChatResponse(
        session_id=session_id,
        stage=str(current_state["stage"]),
        type="onboarding",
        message=result
    )

@app.get("/start/{session_id}")
def start(session_id: str):
    return {
        "session_id": session_id,
        "response": "👋 Welcome to Soko Akili. Are you a Farmer, Seller, or Mixed?"
    }

@app.get("/health")
def health():
    return {"status": "ok"}
