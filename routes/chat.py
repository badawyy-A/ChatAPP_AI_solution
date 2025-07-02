from fastapi import APIRouter, Depends, HTTPException, Path, Request, UploadFile, File, Form
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from models.db import SessionLocal
from services import session_service
from services.chat_service import process_chat
from models.session import Session as SessionModel
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional

router = APIRouter(prefix="/api", tags=["chat"])

class ChatRequest(BaseModel):
    message: Optional[str] = None

class ChatResponse(BaseModel):
    response: Optional[str] = None
    warning: Optional[str] = None

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chat/{session_id}")
async def chat(
    request: Request,
    session_id: str = Path(...),
    db: DBSession = Depends(get_db),
    message: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    format: Optional[str] = None
):
    session = db.query(SessionModel).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session ID")

    user_language = session.user_data.get('language', 'en-US')
    user_input_text = None
    input_type = "unknown"
    input_error = None

    # Handle audio input
    if audio is not None:
        input_type = "audio"
        user_input_text, input_error = process_audio(audio, user_language)
        if input_error:
            return JSONResponse(status_code=400, content={"error": input_error})

    elif message:
        user_input_text = message
        input_type = "text"

    else:
        # Try to get JSON body
        try:
            data = await request.json()
            if data and "message" in data:
                user_input_text = data["message"]
                input_type = "text"
            else:
                return JSONResponse(status_code=400, content={
                    "error": "Input required: Send JSON with 'message' or form-data with 'audio' file."
                })
        except Exception:
            return JSONResponse(status_code=400, content={
                "error": "Input required: Send JSON with 'message' or form-data with 'audio' file."
            })

    response_format = format.lower() if format else "text"
    response_text, warning, audio_fp = process_chat(
        session, user_input_text, input_type, db,
        response_format=response_format, user_language=user_language
    )

    if response_format == "audio":
        if audio_fp:
            return StreamingResponse(audio_fp, media_type="audio/mpeg")
        else:
            return JSONResponse(content={"warning": warning, "response": response_text})
    else:
        return JSONResponse(content={"response": response_text, "warning": warning})

def process_audio(audio: UploadFile, language: str):
    from utils.audio import speech_to_text
    text, error = speech_to_text(audio.file, language=language)
    return text, error
