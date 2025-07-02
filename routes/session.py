from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from models.db import SessionLocal
from services import session_service

router = APIRouter(prefix="/api", tags=["session"])

class StartChatRequest(BaseModel):
    name: str
    email: str = None
    language: str
    # Add other user fields as needed
    # Accept arbitrary user_data
    class Config:
        extra = "allow"

class StartChatResponse(BaseModel):
    session_id: str
    message: str

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/start_chat", response_model=StartChatResponse, status_code=201)
def start_chat(request: StartChatRequest, db: DBSession = Depends(get_db)):
    if not request.language:
        raise HTTPException(status_code=400, detail="User data must include 'language'.")
    user = session_service.get_or_create_user(db, request.dict())
    session = session_service.get_or_create_session(db, user, request.dict())
    return StartChatResponse(session_id=session.id, message="Chat session started.")
