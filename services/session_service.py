from sqlalchemy.orm import Session as DBSession
from models.session import User, Session, ChatHistory
import uuid

__all__ = ["Session", "ChatHistory"]

def get_or_create_user(db: DBSession, user_data: dict):
    # Use email if available, else name, else None
    email = user_data.get('email')
    name = user_data.get('name')
    user = None
    if email:
        user = db.query(User).filter_by(email=email).first()
    elif name:
        user = db.query(User).filter_by(name=name).first()
    if not user:
        user = User(name=name, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def get_or_create_session(db: DBSession, user, user_data: dict):
    session = db.query(Session).filter_by(user_id=user.id).first()
    if not session:
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, user_id=user.id, user_data=user_data)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session

def add_chat_history(db: DBSession, session_id: str, user_message: str, bot_response: str):
    chat = ChatHistory(session_id=session_id, user_message=user_message, bot_response=bot_response)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def get_chat_history(db: DBSession, session_id: str):
    return db.query(ChatHistory).filter_by(session_id=session_id).order_by(ChatHistory.timestamp).all()
