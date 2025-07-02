from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    # Add more user fields as needed
    session = relationship('Session', uselist=False, back_populates='user')

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(String, primary_key=True, index=True)  # UUID string
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    user_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='session')
    chat_history = relationship('ChatHistory', back_populates='session', cascade='all, delete-orphan')

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey('sessions.id'))
    user_message = Column(Text)
    bot_response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session = relationship('Session', back_populates='chat_history')
