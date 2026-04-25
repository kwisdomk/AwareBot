from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from app.state import handle, get
from app.agent import run_agent
from typing import Union
import traceback

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("GOOGLE_API_KEY missing in environment")

app = FastAPI(title="AwareBot", description="Intent-aware market decision agent for Kenyan farmers.")

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
    try:
        session_id = payload.session_id
        message = payload.message

        result = handle(session_id, message)
        current_state = get(session_id)

        # Onboarding complete → run agent
        if isinstance(result, dict):
            print(f"DEBUG: Stage is {current_state.get('stage')}. Entering Gemini Layer...")
            decision = run_agent(result)
            print("DEBUG: Gemini call successful.")
            return ChatResponse(
                session_id=session_id,
                stage=str(current_state["stage"]),
                type="ai_response",
                message=decision
            )

        print(f"DEBUG: Stage is {current_state.get('stage')}. Returning onboarding prompt.")
        if not result:
            result = "⚠️ Something went wrong. Try again."

        return ChatResponse(
            session_id=session_id,
            stage=str(current_state["stage"]),
            type="onboarding",
            message=result
        )
    except Exception as e:
        traceback.print_exc()
        return ChatResponse(
            session_id=payload.session_id,
            stage="error",
            type="error",
            message=f"Backend Error: {str(e)}"
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
